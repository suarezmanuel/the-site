def eval_clause(clause, assignment):
    any_undef = False
    for lit in clause:
        v = abs(lit)
        sign = lit > 0
        if v in assignment:
            if assignment[v] == sign:
                return True
        else:
            any_undef = True
    return None if any_undef else False

def eval_cnf(cnf, assignment):
    for clause in cnf:
        st = eval_clause(clause, assignment)
        if st is False:
            return False
        if st is None:
            return None
    return True



# assignment = {}
# def solve_backtracking(cnf, i):
#     # print(cnf, i)
#     for val in (False, True):
#         assignment[i] = val

#         st = eval_cnf(cnf, assignment)

#         if st is True:
#             return True
#         if st is False:
#             del assignment[i]
#             continue

#         backtrack = solve_backtracking(cnf, i+1)
#         if backtrack:
#             return True
#         del assignment[i]
#     return False

def unit_propagate(cnf, assignment):
    changed = True
    while changed:
        changed = False
        for clause in cnf:
            num_undef = 0
            undef_lit = 0
            sat = False
            for lit in clause:
                v = abs(lit)
                sign = lit > 0
                if v in assignment:
                    if assignment[v] == sign:
                        sat = True
                        break
                else:
                    num_undef += 1
                    undef_lit = lit
            if num_undef == 1 and not sat:
                v = abs(undef_lit)
                val = undef_lit > 0
                assignment[v] = val
                changed = True
    return assignment

def pure_literal_assign(cnf, assignment):
    counts = {}
    for clause in cnf:
        if eval_clause(clause, assignment):
            continue
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                continue
            counts.setdefault(v, 0)
            counts[v] |= (1 if lit > 0 else 2)  # bitmask: 1=positive,2=negative
    for v, mask in counts.items():
        if mask == 1:
            assignment[v] = True
        elif mask == 2:
            assignment[v] = False
    return assignment

def solve(cnf):
    vars = sorted({abs(l) for c in cnf for l in c})

    def recurse(assignment):
        assignment = unit_propagate(cnf, assignment.copy())

        assignment = pure_literal_assign(cnf, assignment.copy())
        
        st = eval_cnf(cnf, assignment)
        if st is True:
            return assignment.copy()
        if st is False:
            return None
        
        unassigned = next(v for v in vars if v not in assignment)
        for val in (True, False):
            assignment[unassigned] = val
            res = recurse(assignment)
            if res is not None:
                return res
            del assignment[unassigned]
        return None

    return recurse({})


# A list of CNFs (each CNF is a list of clauses; each clause is a list of signed ints)
cnfs = [
    # 1. Easy: unit (SAT)
    [[1]],

    # 2. Easy: immediate contradiction (UNSAT)
    [[1], [-1]],

    # 3. Easy: small satisfiable
    [[1, 2], [-1, 3], [-2, -3]],

    # 4. Easy: small unsatisfiable
    [[1, 2], [1, -2], [-1, 2], [-1, -2]],

    # 5. Original example / mixed clause sizes
    [[1, 2, -3], [-1, 4], [-1, -2, -3, 4, 5]],

    # 6. Medium: planted-like example (SAT)
    [[1, 2, 3],
     [-2, -3, 4],
     [5, -6, -1],
     [-4, 3, 6],
     [1, -4, -5],
     [3, 2, -6],
     [-1, -2, 5],
     [-3, 4, 5],
     [2, -3, -6],
     [4, -5, 1],
     [-1, -4, -6],
     [2, 3, -5]],

    # 7. Medium: pigeonhole satisfiable (2 pigeons, 2 holes)
    [[1, 2], [3, 4], [-1, -3], [-2, -4]],

    # 8. Hard-ish: pigeonhole unsat (3 pigeons, 2 holes)
    [[1, 2], [3, 4], [5, 6],
     [-1, -3], [-1, -5], [-3, -5],
     [-2, -4], [-2, -6], [-4, -6]],

    # 9. Hard-ish: small Tseitin on 5-cycle (UNSAT for odd parity)
    [[5, 1], [-5, -1],   # node 0 (charge=1)
     [1, -2], [-1, 2],   # node 1 (charge=0)
     [2, -3], [-2, 3],   # node 2
     [3, -4], [-3, 4],   # node 3
     [4, -5], [-4, 5]],  # node 4

    # 10. Medium: random-looking small 3-SAT
    [[1, -2, 3], [-1, 4, -5], [2, -3, 5], [-4, -2, 6], [-6, 1, -3]],

    # 11. Medium: small UNSAT by forcing contradictory unit
    [[1, 2, 3],
     [1, 2, -3],
     [1, -2, 3],
     [1, -2, -3],
     [-1]],

    # 12. Medium/harder mixed clauses (random-ish)
    [[1, 2, 3],
     [-1, -2, 4],
     [2, -4, 5],
     [-3, 6, -7],
     [7, 8, -1],
     [-2, -5, 8],
     [3, -6, 1],
     [-8, 4, -7],
     [5, -1, 2],
     [-3, -4, -5]]
]

# for cnf in cnfs:
#     print("CNF:", cnf)
#     sat = solve_dpll(cnf)
#     print(sat)
#     # if sat: 
#     #     print(assignment)
#     print()
#     assignment = {}
