def literal_true(lit, assignment):
    v = abs(lit)
    if v not in assignment:
        return None
    return assignment[v] == (lit > 0)

def clause_status(clause, assignment):
    """
    Returns (is_satisfied, num_undef, last_undef_lit)
    """
    num_undef = 0
    last_undef = None
    for lit in clause:
        val = literal_true(lit, assignment)
        if val is True:
            return True, -1, None
        if val is None:
            num_undef += 1
            last_undef = lit
    return False, num_undef, last_undef

def solve(cnf):
    clauses = [list(c) for c in cnf]  # we will append learned clauses
    max_var = max(abs(l) for c in clauses for l in c)

    assignment = {}
    level_of = {}        # var -> decision level
    antecedent = {}  # var -> clause that implied it (None if decision)
    trail = []                # ordered assigned signed literals
    decision_level = 0

    def pick_branch_var():
        for v in range(1, max_var+1):
            if v not in assignment:
                return v
        return None

    def bcp():
        """
        Boolean constraint propagation.
        Returns None if no conflict, else returns conflicting clause (the clause that's falsified).
        New propagated variables get antecedent set to the clause they came from and level = decision_level.
        """
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                sat, num_undef, last_undef = clause_status(clause, assignment)
                if sat:
                    continue
                if num_undef == 0:
                    # conflict
                    return clause
                if num_undef == 1:
                    lit = last_undef
                    if lit is None:
                        continue
                    v = abs(lit)
                    val = lit > 0
                    if v in assignment:
                        # check consistency
                        if assignment[v] != val:
                            return clause
                        continue
                    # propagate
                    assignment[v] = val
                    level_of[v] = decision_level
                    antecedent[v] = clause
                    trail.append(lit if val else -v)
                    changed = True
        return None

    def analyze(conflict_clause):
        """
        Conflict analysis (First-UIP style). Return (learned_clause, backtrack_level).
        We'll implement the standard loop resolving with antecedents until learned clause has one literal
        from current decision level. The learned clause is returned as a list of ints.
        """
        learned = set(conflict_clause)
        # count literals in learned at current level
        def count_current(learned_set):
            cnt = 0
            for lit in learned_set:
                v = abs(lit)
                if v in level_of and level_of[v] == decision_level:
                    cnt += 1
            return cnt

        # Helper to resolve learned with antecedent on variable pivot
        def resolve(learned_set, antecedent_clause, pivot_var):
            # find literal of pivot in learned_set and in antecedent_clause
            lit_in_learned = next(l for l in learned_set if abs(l) == pivot_var)
            lit_in_ante = next(l for l in antecedent_clause if abs(l) == pivot_var)
            # resolution: (learned ∪ antecedent) \ {lit_in_learned, lit_in_ante}
            new = (learned_set.union(antecedent_clause)) - {lit_in_learned, lit_in_ante}
            return set(new)

        # iterate over trail backwards, resolving until first-UIP
        while True:
            num_cur = count_current(learned)
            if num_cur <= 1:
                break
            # find latest assigned variable on trail that appears in learned
            pivot_var = None
            for lit in reversed(trail):
                v = abs(lit)
                if any(abs(l2) == v for l2 in learned):
                    pivot_var = v
                    break
            if pivot_var is None:
                break  # shouldn't happen
            ant = antecedent.get(pivot_var)
            if ant is None:
                # pivot was a decision literal; remove it from learned (no antecedent)
                # this reduces the count of current-level literals
                learned = {l for l in learned if abs(l) != pivot_var}
            else:
                learned = resolve(learned, ant, pivot_var)

        # Now compute backtrack level: maximum level among literals in learned except the one at current level
        learned_list = list(learned)
        # find the literal that belongs to current level (asserting literal)
        asserting = None
        for lit in learned_list:
            v = abs(lit)
            if level_of.get(v, -1) == decision_level:
                asserting = lit
                break
        # compute backtrack level
        backtrack_level = 0
        for lit in learned_list:
            v = abs(lit)
            lv = level_of.get(v, 0)
            if lv != decision_level:
                if lv > backtrack_level:
                    backtrack_level = lv
        # return learned clause (list) and backtrack level
        return list(learned), backtrack_level

    def backtrack_to(level: int):
        nonlocal decision_level
        # unassign variables with level > level
        while trail:
            lit = trail[-1]
            v = abs(lit)
            if level_of.get(v, 0) > level:
                trail.pop()
                if v in assignment:
                    del assignment[v]
                if v in level_of:
                    del level_of[v]
                if v in antecedent:
                    del antecedent[v]
            else:
                break
        decision_level = level

    # main CDCL loop
    while True:
        confl = bcp()
        if confl is not None:
            if decision_level == 0:
                return None  # unsatisfiable
            learned, bt_level = analyze(confl)
            # add learned clause
            clauses.append(learned)
            # backjump
            backtrack_to(bt_level)
            # After backtracking, the learned clause should become unit and be propagated by bcp
            # To ensure that, we don't explicitly force it; next loop iteration bcp() will do it.
            continue

        # check satisfied
        if all(clause_status(c, assignment)[0] for c in clauses):
            return assignment.copy()
        # pick branching variable
        v = pick_branch_var()
        if v is None:
            return assignment.copy()
        # new decision level
        decision_level += 1
        # assign v = True (branch heuristic could be improved)
        assignment[v] = True
        level_of[v] = decision_level
        antecedent[v] = None
        trail.append(v)

# Example:
# print(solve_cdcl([[1,2,-3],[-1,4],[-1,-2,-3,4,5]]))
