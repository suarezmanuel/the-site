# real_solver.py
"""
real_solver.py

Provides:
    solve(cnf: List[List[int]]) -> bool

Uses the PySAT library (Minisat backend) to solve CNF formulas.
Each clause should be a list of integers (DIMACS-style literals).
Returns True if satisfiable, False if unsatisfiable.

Install PySAT if needed:
    pip install python-sat
"""

from typing import List

__all__ = ["solve"]

def _validate_cnf(cnf):
    if not isinstance(cnf, list):
        raise TypeError("cnf must be a list of clauses")
    for i, cl in enumerate(cnf):
        if not isinstance(cl, list):
            raise TypeError(f"clause #{i} is not a list")
        for lit in cl:
            if not isinstance(lit, int):
                raise TypeError(f"literal {lit!r} in clause #{i} is not an int")

def solve(cnf: List[List[int]]) -> bool:
    """
    Solve the given CNF using a native SAT solver (via PySAT).

    Parameters
    ----------
    cnf : List[List[int]]
        CNF formula as list of clauses, each clause is a list of ints.
        e.g. [[1, -3], [2], [-1, 3, 4]]

    Returns
    -------
    bool
        True if satisfiable, False if unsatisfiable.

    Raises
    ------
    ImportError
        If python-sat (PySAT) is not installed.
    TypeError
        If cnf is not in expected format.
    """
    _validate_cnf(cnf)

    # Trivial checks
    # empty CNF (no clauses) is satisfiable
    if len(cnf) == 0:
        return True
    # if any clause is empty, CNF is unsatisfiable
    for cl in cnf:
        if len(cl) == 0:
            return False

    # Try to import PySAT
    try:
        # prefer Minisat22 if available
        from pysat.solvers import Minisat22
    except Exception as e:
        raise ImportError(
            "PySAT (python-sat) is required. Install with: pip install python-sat\n"
            f"Import error: {e}"
        )

    # PySAT accepts an iterable of clauses for bootstrap_with
    try:
        with Minisat22(bootstrap_with=cnf) as solver:
            sat = solver.solve()
            return bool(sat)
    except Exception as e:
        # Re-raise as RuntimeError to be explicit for the caller
        raise RuntimeError(f"SAT solver error: {e}")
