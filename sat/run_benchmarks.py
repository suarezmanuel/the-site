#!/usr/bin/env python3
"""
run_benchmarks.py - improved

Runs a solver on every .cnf in a benchmarks folder with a timeout,
compares the solver result to ground truth when available, and alerts
the user about any wrong answers (sat vs unsat).

By default imports solver module 'real_solver' and calls 'solve'.
You can point --solver to any importable module that exposes a 'solve' function.

Outputs:
  - results_checked.csv : per-instance results + expected + mismatch flag
  - mismatches.csv      : only the mismatches (sat/unsat disagreements)

Ground truth detection order:
  1) --gold CSV file (filename, expected)
  2) sidecar files next to the CNF: .ans, .out, .expected, .result
  3) filename contains 'sat' or 'unsat'
  4) otherwise expected is 'unknown'
"""

import argparse
import glob
import importlib
import multiprocessing as mp
import os
import time
import csv
import sys
from typing import Optional, Tuple, Dict

# -----------------------
# DIMACS parser
# -----------------------
def parse_dimacs(path: str):
    clauses = []
    current = []
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                continue
            parts = line.split()
            for token in parts:
                try:
                    lit = int(token)
                except ValueError:
                    continue
                if lit == 0:
                    if current:
                        clauses.append(current)
                        current = []
                else:
                    current.append(lit)
    if current:
        clauses.append(current)
    return clauses

# -----------------------
# Worker process that calls the solver
# -----------------------
def _worker(cnf, solver_name: str, out_q: mp.Queue):
    """
    Worker runs inside a separate process so it can be killed on timeout.
    Puts a tuple (result_str, elapsed_seconds, note) into out_q.
    result_str is one of: "sat", "unsat", "timeout" (shouldn't appear here), "error"
    """
    import importlib
    import time as _time
    try:
        solver_mod = importlib.import_module(solver_name)
    except Exception as e:
        out_q.put(("error", 0.0, f"import-error: {e}"))
        return

    # find solve function
    solve_fn = getattr(solver_mod, "solve", None)
    if solve_fn is None:
        # also support older style name used earlier
        solve_fn = getattr(solver_mod, "solve_backtracking", None)

    if solve_fn is None:
        out_q.put(("error", 0.0, "no 'solve' function in solver module"))
        return

    start = _time.perf_counter()
    try:
        # Try calling solve(cnf)
        try:
            res = solve_fn(cnf)
        except TypeError:
            # maybe signature is solve(cnf, start_index)
            res = solve_fn(cnf, 1)
    except Exception as e:
        elapsed = _time.perf_counter() - start
        out_q.put(("error", elapsed, f"runtime-error: {e}"))
        return

    elapsed = _time.perf_counter() - start
    # Interpret result: truthy => sat, falsy => unsat
    try:
        sat_bool = bool(res)
        out_q.put(("sat" if sat_bool else "unsat", elapsed, None))
    except Exception as e:
        out_q.put(("error", elapsed, f"bad-return-value: {e}"))

# -----------------------
# Run one CNF with timeout
# -----------------------
def run_one(cnf, solver_name: str, timeout_seconds: float = 10.0) -> Tuple[str, Optional[float], Optional[str]]:
    q = mp.Queue()
    p = mp.Process(target=_worker, args=(cnf, solver_name, q))
    p.start()
    p.join(timeout_seconds)
    if p.is_alive():
        p.terminate()
        p.join()
        return ("timeout", None, "killed-after-timeout")
    else:
        # process finished; read queue
        try:
            res, elapsed, note = q.get_nowait()
            return (res, elapsed, note)
        except Exception:
            return ("error", None, "no-result-in-queue")

# -----------------------
# Ground-truth discovery
# -----------------------
def load_gold_map(gold_csv: Optional[str]) -> Dict[str, str]:
    """
    Load CSV with two columns: filename, expected
    expected should be 'sat' or 'unsat' (case-insensitive)
    """
    mapping = {}
    if not gold_csv:
        return mapping
    if not os.path.exists(gold_csv):
        print(f"[WARN] gold CSV '{gold_csv}' not found. Ignoring.", file=sys.stderr)
        return mapping
    with open(gold_csv, newline='') as f:
        rdr = csv.reader(f)
        for row in rdr:
            if not row:
                continue
            if len(row) < 2:
                continue
            fname = row[0].strip()
            exp = row[1].strip().lower()
            if exp not in ("sat", "unsat"):
                continue
            mapping[fname] = exp
    return mapping

def read_sidecar_expected(cnf_path: str) -> Optional[str]:
    """
    Checks for sidecar files next to CNF with common extensions and
    tries to parse 'sat'/'unsat' from their contents.
    """
    base = cnf_path
    candidates = [base + ext for ext in (".ans", ".out", ".expected", ".result", ".sat")]
    # also check files with same base name but different extension: base_name + .ans etc
    base_name, _ = os.path.splitext(cnf_path)
    candidates += [base_name + ext for ext in (".ans", ".out", ".expected", ".result", ".sat")]
    for cand in candidates:
        if os.path.exists(cand):
            try:
                with open(cand, "r") as f:
                    data = f.read().lower()
                    if "unsat" in data:
                        return "unsat"
                    if "sat" in data:
                        return "sat"
            except Exception:
                continue
    return None

def expected_from_filename(path: str) -> Optional[str]:
    n = os.path.basename(path).lower()
    print(f'path={path}')
    if "unsat" in n or "unsatisf" in n:
        return "unsat"
    if "sat" in n or "satisf" in n:
        return "sat"
    return None

def find_expected(path: str, gold_map: Dict[str,str]) -> str:
    # 1) gold_map exact filename match
    bname = os.path.basename(path)
    if bname in gold_map:
        return gold_map[bname]
    # 2) sidecar files
    s = read_sidecar_expected(path)
    if s:
        return s
    # 3) filename heuristic
    s2 = expected_from_filename(path)
    print(f'expected={s2}')
    if s2:
        return s2
    return "unknown"

# -----------------------
# Main
# -----------------------
def main():
    parser = argparse.ArgumentParser(description="Run SAT solver on benchmarks and compare to ground truth.")
    parser.add_argument("--benchmarks", "-b", default="benchmarks", help="folder with .cnf files")
    parser.add_argument("--solver", "-s", default="dpll", help="solver module name to import (must expose solve(cnf) or solve_backtracking)")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="timeout seconds per instance")
    parser.add_argument("--gold", "-g", default="correct_results.csv", help="optional ground-truth CSV (filename,expected) where expected is sat/unsat")
    parser.add_argument("--out", "-o", default="results_checked.csv", help="output CSV file")
    parser.add_argument("--mismatches", default="mismatches.csv", help="mismatches CSV file")
    args = parser.parse_args()

    bench_glob = os.path.join(args.benchmarks, "*.cnf")
    files = sorted(glob.glob(bench_glob))
    if not files:
        print(f"No .cnf files found in {args.benchmarks}", file=sys.stderr)
        sys.exit(1)

    # Try to set 'spawn' for safety across platforms
    try:
        mp.set_start_method("spawn")
    except RuntimeError:
        pass

    gold_map = load_gold_map(args.gold)

    with open(args.out, "w", newline="") as out_f, open(args.mismatches, "w", newline="") as mm_f:
        writer = csv.writer(out_f)
        mm_writer = csv.writer(mm_f)
        writer.writerow(["filename", "result", "time_seconds", "note", "expected", "mismatch"])
        mm_writer.writerow(["filename", "result", "time_seconds", "note", "expected", "mismatch"])

        for fp in files:
            print(f"Solving {fp} ...")
            try:
                cnf = parse_dimacs(fp)
            except Exception as e:
                print(f"  [ERROR] parse error for {fp}: {e}", file=sys.stderr)
                writer.writerow([fp, "error", "N/A", f"parse-error: {e}", "unknown", "unknown"])
                continue

            result, elapsed, note = run_one(cnf, args.solver, timeout_seconds=args.timeout)
            time_str = f"{elapsed:.6f}" if elapsed is not None else "N/A"

            expected = find_expected(fp, gold_map)  # sat/unsat/unknown

            # Determine mismatch:
            # - If expected unknown -> mismatch = unknown
            # - If result is 'timeout' or 'error' -> mismatch = unknown (we don't call these 'wrong' per request)
            # - If result in sat/unsat and expected is sat/unsat -> compare, if different -> mismatch=yes
            mismatch = "unknown"
            if expected in ("sat", "unsat"):
                if result in ("sat", "unsat"):
                    mismatch = "yes" if result != expected else "no"
                else:
                    mismatch = "unknown"

            writer.writerow([fp, result, time_str, note or "", expected, mismatch])

            if mismatch == "yes":
                # Alert user: print obvious banner and write to mismatches file
                banner = (
                    "\n" + "="*80 + "\n"
                    f"[MISMATCH] {fp}\n"
                    f"  expected : {expected}\n"
                    f"  solver   : {result}\n"
                    f"  time     : {time_str}\n"
                    f"  note     : {note or ''}\n"
                    + "="*80 + "\n"
                )
                print(banner, file=sys.stderr)
                mm_writer.writerow([fp, result, time_str, note or "", expected, mismatch])

            else:
                print(f"  -> {result} (time={time_str}) expected={expected} mismatch={mismatch}")

    print(f"\nDone. Wrote checked results to {args.out} and mismatches to {args.mismatches}")

if __name__ == "__main__":
    main()
