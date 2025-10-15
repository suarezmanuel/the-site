---
title: "How SAT Solvers Work"
tags: ['cs', 'python']
---


# How SAT Solvers Work
## The SAT problem

The Boolean Satisfiability Problem (SAT) is a fundamental problem in computer science and mathematical logic. It asks whether there exists an assignment of truth values (true or false) to variables in a given Boolean formula such that the entire formula evaluates to true. 
SAT has applications in program verification, AI, and cryptography, which means that solving it is crucial in the world of computer science. Unfortunatly SAT is NP-complete, meaning that if an efficient algorithm exists for SAT, then efficient algorithms exist for all problems in the NP class. It is assumed that there are no efficient algorithms for NP-complete problems, and while it might sound discouraging, in practice modern SAT solvers are remarkably effective.

To understand SAT solvers we first have to look at a specific case, CNF (conjunctive normal form).
We say that a formula is CNF if it is a conjunction of clauses, where each clause is a disjunction of literals.
For example, the formula $(x_1\land \lnot x_2)\lor (x_3)$ is not CNF because the first clause is a conjunction and because the formula itself is a disjunction of clauses. On the other hand, $(x_1\lor \lnot x_2)\land (x_3)$ is CNF.

At first CNF looks too easy, but in fact, this version of the problem is also NP-complete and we will see how to use solvers that are only suitable in these cases to solve the general SAT.

## Beofre we start
It is important to define how literals and formulas are represented in code. A literal is represented by a number, positive if the literal is positive and negative otherwise. For example $x_3$ will be written as $3$ and $\lnot x_7$ as $-7$. A clause is a list of literals, so $(\lnot x_2 \lor x_4 \lor \lnot x_7)$ is represented as $[-2, 4, -7]$. Similarly, a CNF formula is a list of clauses, this means that the formula $(\lnot x_2 \lor x_4 \lor \lnot x_7) \land (x_1) \land (x_2 \lor x_4)$ will be seen in code as $[[-2, 4, -7], [1], [2, 4]]$.

We can now implement the methods 'eval_clause' and 'eval_cnf' that evaluate an assignment on a clause and on a full CNF formula respectively. We will use these functions throughout this page.

++
/\ The methods return `True` if the assignment satisfies the clause/formula, `False` if the clause/formula has a false value under the assignment, and `None` if it cannot know (can happen when the assignment is not complete, meaning it does not assign value to every variable).
```python
def eval_clause(clause, assignment):
    any_undef = False
    for literal in clause:
        v = abs(literal)
        sign = literal > 0
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
```
++

Because a clause is always a disjunction, even if we find just one satisfied literal - the clause is satisfied. Conversely, a CNF formula is a conjunction, so if we find one clause that is not satisfied - the formula is not satisfied.

## Backtracking
The first method we are going to look at is called *Backtracking*. This method is close to the naive algorithm of looping over all possible assignments. The only difference between the 2 methods is that with backtracking we can find a conflict early: if the formula includes the clause $(x_1)$ then we can find in the start that the assignment to $x_1$ must be 'true'. This means we don't have to check both the assignment that assigns $x_1$ 'false' and $x_2$ 'true' and the assignment that assigns $x_1$ 'false' and $x_2$ 'false. 

We will look at an implementation of this algorithm in python.

```python
assignment = {}
def solve(cnf, i):
    for val in (False, True):
        assignment[i] = val

        st = eval_cnf(cnf, assignment)

        # if a true assignment was found the proposition is SAT
        if st is True: 
            return True
        if st is False:
            del assignment[i]
            continue

        backtrack = solve(cnf, i+1)
        if backtrack:
            return True
        del assignment[i]
    # if no assignment satisfies the formula it is UNSAT
    return False
```

This algorithm can already solve small SAT problems but we can do better.

## DPLL
DPLL (Davis–Putnam–Logemann–Loveland) builds on backtracking by implementing a few simple rules. In Backtracking, the algorithm guesses a value for every literal until it encounters a conflict, we can be smarter than that. In the example above, where we have a clause $(x_1)$, we can immediatly infer that $x_1$ must be assigned `True`. In fact, this logic can also be applied in a more general case. For example, if we have the clause $(x_1 \lor x_2)$ and our current assignment gives $x_2$ the value `False` then we can also infer that $x_1$ must be `True`.

Let's look at another example: $$(\lnot x_2 \lor x_1 \lor \lnot x_3) \land (x_1) \land (x_2 \lor x_3)$$ Is there any reason here to assign $x_1$ `False`? No because the literal $\lnot x_1$ does not appear in the formula. It might not have to be set to `True`, but there is no reason not to. This logic can be extended: after we know to assign $x_1$ `True`, we can ignore the first clause because it is now satisfied. That means that the literal $\lnot x_2$ also does not appear (remember we ignore the first clause now) so using the same logic we can assign it `True` and we found a satisfying assignment!

We can now write the 2 rules:
1. `Unit Propagation`: If an unsatisfied clause has exactly one unassigned literal, then that literal must be assigned a positive value.
2. `Pure Literal Elimination`: If a variable appears in unsatisfied clauses only as a positive (or only as a negative), assign it accordingly.

We now take a look at the implementation of DPLL, starting with the function for unit propagation:

```python
def unit_propagate(cnf, assignment):
    changed = True
    while changed:
        changed = False
        for clause in cnf:
            num_undef = 0
            undef_lit = 0
            for lit in clause:
                v = abs(lit)
                sign = lit > 0
                if v in assignment:
                    # skip satisfied clauses
                    if assignment[v] == sign:
                        break
                else:
                    num_undef += 1
                    undef_lit = lit
            if num_undef == 1:
                # we found an unsatisfied clause 
                # with one undefined literal
                v = abs(undef_lit)
                val = undef_lit > 0
                assignment[v] = val
                changed = True
    return assignment
```
This function loops over every clause, skipping satisfied ones, and if it finds one with just one undefined literal it knows we have to assign it a positive value.
We now see the pure literal elimination function:
```python
def pure_literal_assign(cnf, assignment):
    counts = {}
    for clause in cnf:
        # ignore satisfied clauses 
        if eval_clause(clause, assignment):
            continue
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                # skip assigned variables
                continue
            counts.setdefault(v, 0)
            # bitmask: 01=positive,10=negative
            counts[v] |= (0b01 if lit > 0 else 0b10)  
    for v, mask in counts.items():
        if mask == 0b01:
            assignment[v] = True
        elif mask == 0b10:
            assignment[v] = False
    return assignment
```
This function records for every encounter with an unassigned variable, whether it was positive or negative while ignoring satisfied clauses. At the end, it assigns negative/positive value for variables that appeared only negatively/positively.  

Finally, we can implement the main function:
```python
def solve_dpll(cnf):
    vars = sorted({abs(l) for c in cnf for l in c})

    def recurse(assignment):
        assignment = unit_propagate(cnf, assignment)

        assignment = pure_literal_assign(cnf, assignment)
        
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
```

There are a few important things to note here. First, the function 'recurse' starts by calling unit_propagate and pure_literal_assign. This is because these functions are pure logical assessments about the formula and assignment. Only after calling them do we check whether the assignment gives a true or false value to the formula. Second, although we would like to infer each assignment logically we cannot always do that, therefore, we have the last part of the recurse function where we choose a variable and check both assignments. Because recursive calls only appear in that part, backtracking only backtracks guessed values and not values that were assigned in unit propagation or pure literal elimination. 
