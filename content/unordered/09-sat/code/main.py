from dpll import solve
import sys

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


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    cnf = parse_dimacs(input_path)

    with open(output_path, "w") as fd:
        result = solve(cnf, fd)

    print("SATISFIABLE" if result else "UNSATISFIABLE")

if __name__ == "__main__":
    main()