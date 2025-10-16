# returns (is_satisfied, num_undef, last_undef_lit)
def clause_status(clause, assignment):
    num_undef = 0
    last_undef = None
    for lit in clause:
        v = abs(lit)
        if v not in assignment:
            num_undef += 1
            last_undef = lit
        if assignment[v] == (lit > 0):
            return True, -1, None
    return False, num_undef, last_undef

def solve(cnf):
    max_var = max(abs(l) for c in cnf for l in c)
    assignment = {}
    trail = []
    antecedent = {}
    decision_level = 0
    decided_at = {}
    
    def search_for_conflict():
        changed = True
        while changed:
            changed = False
            for clause in cnf:
                st, num_undef, last_undef = clause_status(clause, assignment)
                if st is True:
                    continue

                if num_undef == 0:
                    return clause
                if not last_undef:
                    return None
                if num_undef == 1:
                    v = abs(last_undef)
                    sign = last_undef > 0
                    assignment[v] = sign
                    antecedent[v] = clause
                    trail.append(last_undef)
                    decided_at[v] = decision_level
                    changed = True
        return None


    def analyze(conflict):
        learned = set(conflict)
        
        def count_level(clause):
            count = 0
            for lit in clause:
                if decided_at[abs(lit)] == decision_level:
                    count += 1
            return count
        
        while count_level(learned) > 1:
            next_lit = next(l for l in reversed(trail) if -l in learned)

            ant = antecedent[abs(next_lit)]

            learned = learned.union(set(ant)) - {next_lit, -next_lit}

        cnf.append(list(learned))


    def backjump(level):
        num_assigned = len(trail)

        var = abs(trail[num_assigned - 1])
        while decided_at[var] > level:
            del assignment[var]
            trail.pop()
            num_assigned -= 1
            if num_assigned == 0:
                break
            var = abs(trail[num_assigned - 1])

    while True:
        conflict = search_for_conflict()
        if conflict:
            if decision_level == 0:
                return False
            
            analyze(conflict)

            decision_level -= 1
            backjump(decision_level)

            continue

        st = all(clause_status(clause, assignment)[0] for clause in cnf)
        if st is True:
            return assignment.copy()
        
        decision_level += 1
        
        next_var = next(v+1 for v in range(max_var) if v+1 not in assignment)
        assignment[next_var] = True
        decided_at[next_var] = decision_level
        antecedent[next_var] = None
        trail.append(next_var)

# def solve(cnf):
#     clauses = [list(c) for c in cnf]  # we will append learned clauses
#     max_var = max(abs(l) for c in clauses for l in c)

#     assignment = {}
#     level_of = {}        # var -> decision level
#     antecedent = {}  # var -> clause that implied it (None if decision)
#     trail = []                # ordered assigned signed literals
#     decision_level = 0

#     def pick_branch_var():
#         for v in range(1, max_var+1):
#             if v not in assignment:
#                 return v
#         return None

#     def bcp():
#         """
#         Boolean constraint propagation.
#         Returns None if no conflict, else returns conflicting clause (the clause that's falsified).
#         New propagated variables get antecedent set to the clause they came from and level = decision_level.
#         """
#         changed = True
#         while changed:
#             changed = False
#             for clause in clauses:
#                 sat, num_undef, last_undef = clause_status(clause, assignment)
#                 if sat:
#                     continue
#                 if num_undef == 0:
#                     # conflict
#                     return clause
#                 if num_undef == 1:
#                     lit = last_undef
#                     if lit is None:
#                         continue
#                     v = abs(lit)
#                     val = lit > 0
#                     if v in assignment:
#                         # check consistency
#                         if assignment[v] != val:
#                             return clause
#                         continue
#                     # propagate
#                     assignment[v] = val
#                     level_of[v] = decision_level
#                     antecedent[v] = clause
#                     trail.append(lit if val else -v)
#                     changed = True
#         return None

#     def analyze(conflict_clause):
#         """
#         Conflict analysis (First-UIP style). Return (learned_clause, backtrack_level).
#         We'll implement the standard loop resolving with antecedents until learned clause has one literal
#         from current decision level. The learned clause is returned as a list of ints.
#         """
#         learned = set(conflict_clause)
#         # count literals in learned at current level
#         def count_current(learned_set):
#             cnt = 0
#             for lit in learned_set:
#                 v = abs(lit)
#                 if v in level_of and level_of[v] == decision_level:
#                     cnt += 1
#             return cnt

#         # Helper to resolve learned with antecedent on variable pivot
#         def resolve(learned_set, antecedent_clause, pivot_var):
#             # find literal of pivot in learned_set and in antecedent_clause
#             lit_in_learned = next(l for l in learned_set if abs(l) == pivot_var)
#             lit_in_ante = next(l for l in antecedent_clause if abs(l) == pivot_var)
#             # resolution: (learned ∪ antecedent) \ {lit_in_learned, lit_in_ante}
#             new = (learned_set.union(antecedent_clause)) - {lit_in_learned, lit_in_ante}
#             return set(new)

#         # iterate over trail backwards, resolving until first-UIP
#         while True:
#             num_cur = count_current(learned)
#             if num_cur <= 1:
#                 break
#             # find latest assigned variable on trail that appears in learned
#             pivot_var = None
#             for lit in reversed(trail):
#                 v = abs(lit)
#                 if any(abs(l2) == v for l2 in learned):
#                     pivot_var = v
#                     break
#             if pivot_var is None:
#                 break  # shouldn't happen
#             ant = antecedent.get(pivot_var)
#             if ant is None:
#                 # pivot was a decision literal; remove it from learned (no antecedent)
#                 # this reduces the count of current-level literals
#                 learned = {l for l in learned if abs(l) != pivot_var}
#             else:
#                 learned = resolve(learned, ant, pivot_var)

#         # Now compute backtrack level: maximum level among literals in learned except the one at current level
#         learned_list = list(learned)
#         # find the literal that belongs to current level (asserting literal)
#         asserting = None
#         for lit in learned_list:
#             v = abs(lit)
#             if level_of.get(v, -1) == decision_level:
#                 asserting = lit
#                 break
#         # compute backtrack level
#         backtrack_level = 0
#         for lit in learned_list:
#             v = abs(lit)
#             lv = level_of.get(v, 0)
#             if lv != decision_level:
#                 if lv > backtrack_level:
#                     backtrack_level = lv
#         # return learned clause (list) and backtrack level
#         return list(learned), backtrack_level

#     def backtrack_to(level: int):
#         nonlocal decision_level
#         # unassign variables with level > level
#         while trail:
#             lit = trail[-1]
#             v = abs(lit)
#             if level_of.get(v, 0) > level:
#                 trail.pop()
#                 if v in assignment:
#                     del assignment[v]
#                 if v in level_of:
#                     del level_of[v]
#                 if v in antecedent:
#                     del antecedent[v]
#             else:
#                 break
#         decision_level = level

#     # main CDCL loop
#     while True:
#         confl = bcp()
#         if confl is not None:
#             if decision_level == 0:
#                 return None  # unsatisfiable
#             learned, bt_level = analyze(confl)
#             # add learned clause
#             clauses.append(learned)
#             # backjump
#             backtrack_to(bt_level)
#             # After backtracking, the learned clause should become unit and be propagated by bcp
#             # To ensure that, we don't explicitly force it; next loop iteration bcp() will do it.
#             continue

#         # check satisfied
#         if all(clause_status(c, assignment)[0] for c in clauses):
#             return assignment.copy()
#         # pick branching variable
#         v = pick_branch_var()
#         if v is None:
#             return assignment.copy()
#         # new decision level
#         decision_level += 1
#         # assign v = True (branch heuristic could be improved)
#         assignment[v] = True
#         level_of[v] = decision_level
#         antecedent[v] = None
#         trail.append(v)

# Example:
# print(solve_cdcl([[1,2,-3],[-1,4],[-1,-2,-3,4,5]]))


# decision_level = 2
# decided_at = {1:1, 2:1, 3:1, 4:1, 5:1, 6:2, 7:2, 8:2, 9:2, 10:2, 12:2, 11:2}
# trail = [1, -2, 3, -4, 5, -6, -7, 8, -9, 10, 11, -12]
# antecedent = {2:[-1,-2], 3:[-1,3], 4:[-3,-4], 5:[2,4,5], 7:[-5,6,-7], 8:[2,7,8], 9:[-8,-9], 10:[-8,10], 11:[9,-10,11], 12:[-10,-12]}

# def analyze(conflict):
#         learned = set(conflict)
        
#         def count_level(clause):
#             count = 0
#             for lit in clause:
#                 if decided_at[abs(lit)] == decision_level:
#                     count += 1
#             return count
        
#         while count_level(learned) > 1:
#             # print(learned)
#             # print(trail)
#             next_lit = next(l for l in reversed(trail) if -l in learned)

#             ant = antecedent[abs(next_lit)]

#             learned = learned.union(set(ant)) - {next_lit, -next_lit}

#         print(list(learned))

# analyze([-11, 12])

# cnfs = [
#     # 1. Easy: unit (SAT)
#     [[1]],

#     # 2. Easy: immediate contradiction (UNSAT)
#     [[1], [-1]],

#     # 3. Easy: small satisfiable
#     [[1, 2], [-1, 3], [-2, -3]],

#     # 4. Easy: small unsatisfiable
#     [[1, 2], [1, -2], [-1, 2], [-1, -2]],

#     # 5. Original example / mixed clause sizes
#     [[1, 2, -3], [-1, 4], [-1, -2, -3, 4, 5]],

#     # 6. Medium: planted-like example (SAT)
#     [[1, 2, 3],
#      [-2, -3, 4],
#      [5, -6, -1],
#      [-4, 3, 6],
#      [1, -4, -5],
#      [3, 2, -6],
#      [-1, -2, 5],
#      [-3, 4, 5],
#      [2, -3, -6],
#      [4, -5, 1],
#      [-1, -4, -6],
#      [2, 3, -5]],

#     # 7. Medium: pigeonhole satisfiable (2 pigeons, 2 holes)
#     [[1, 2], [3, 4], [-1, -3], [-2, -4]],

#     # 8. Hard-ish: pigeonhole unsat (3 pigeons, 2 holes)
#     [[1, 2], [3, 4], [5, 6],
#      [-1, -3], [-1, -5], [-3, -5],
#      [-2, -4], [-2, -6], [-4, -6]],

#     # 9. Hard-ish: small Tseitin on 5-cycle (UNSAT for odd parity)
#     [[5, 1], [-5, -1],   # node 0 (charge=1)
#      [1, -2], [-1, 2],   # node 1 (charge=0)
#      [2, -3], [-2, 3],   # node 2
#      [3, -4], [-3, 4],   # node 3
#      [4, -5], [-4, 5]],  # node 4

#     # 10. Medium: random-looking small 3-SAT
#     [[1, -2, 3], [-1, 4, -5], [2, -3, 5], [-4, -2, 6], [-6, 1, -3]],

#     # 11. Medium: small UNSAT by forcing contradictory unit
#     [[1, 2, 3],
#      [1, 2, -3],
#      [1, -2, 3],
#      [1, -2, -3],
#      [-1]],

#     # 12. Medium/harder mixed clauses (random-ish)
#     [[1, 2, 3],
#      [-1, -2, 4],
#      [2, -4, 5],
#      [-3, 6, -7],
#      [7, 8, -1],
#      [-2, -5, 8],
#      [3, -6, 1],
#      [-8, 4, -7],
#      [5, -1, 2],
#      [-3, -4, -5]]
# ]

# for cnf in cnfs:
#     print("CNF:", cnf)
#     sat = cdcl(cnf)
#     print(sat)
#     # if sat: 
#     #     print(assignment)
#     print()
#     assignment = {}
