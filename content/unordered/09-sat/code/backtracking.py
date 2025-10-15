# evaluates assignment on clause
# return True if one literal is True
# return False if all literals are False
# return None if some literals are undefined and none is True
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

# -16
# assignment[16] = False

def eval_cnf(cnf, assignment):
    for clause in cnf:
        st = eval_clause(clause, assignment)
        if st is False:
            return False
        if st is None:
            return None
    return True


assignment = {}
def solve_backtracking(cnf, i):
    # print(cnf, i)
    for val in (False, True):
        assignment[i] = val

        st = eval_cnf(cnf, assignment)

        if st is True:
            return True
        if st is False:
            del assignment[i]
            continue

        backtrack = solve_backtracking(cnf, i+1)
        if backtrack:
            return True
        del assignment[i]
    return False