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

We also need the function 'clause status' that gets a clause and an assignment and returns 3 values. Whether the assignment satisfies the clause, the number of unassigned literals in the clause, and the last unassigned literal.
```python
# returns (is_satisfied, num_undef, last_undef_lit)
def clause_status(clause, assignment):
    num_undef = 0
    last_undef = None
    for lit in clause:
        v = abs(lit)
        if v not in assignment:
            num_undef += 1
            last_undef = lit
        elif assignment[v] == (lit > 0):
            return True, -1, None
    return False, num_undef, last_undef
```


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
            st, num_undef, undef_lit = clause_status(clause, assignment)
            # if clause is unsatisfied with one unassigned
            if num_undef == 1 and not st and undef_lit:
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

## CDCL
To understand the motivation behind CDCL (conflict driven clause learning) we start with an example: $$ (x_1\lor x_4)\land (x_2 \lor \lnot x_4)\land (x_3 \land x_5)$$ 
One possible run on this formula is as follows:
Guess $x_1=False$, Guess $x_2=False$, Guess $x_3=False$, now unit propagate on $(x_1\lor x_4)$ and infer that $x_4=True$. At this point we reached a conflict at $(x_2 \lor \lnot x_4)$.

We can see that this conflict arose when we chose both $x_1$ and $x_2$ to be negative but our algorithm will backtrack on the decision $x_3=False$ and will eventually find a similar conflict. We would want our algorithm to learn the new clause $(x_1\lor x_2)$ and backtrack 2 levels in this case

Let's put our task into words. First, when DPLL encounters a conflict (an UNSAT assignment) it just backtracks without understanding and remembering the cause for the conflict. This causes the algorithm to make the same mistakes multiple times. Furthermore, only backtracking once when a conflict occurs might keep an assignment that is doomed to fail. CDCL answers this problems by analyzing conflicts, remebering them, and `backjumping` to the cause of the conflict.

### The Algorithm
In order to analyze conflicts and find their root cause we have to keep more data about our search. First, we must remember why a variable has certain value in the current assignment. This is done using a trail. When we decide a value for a literal $l$ we add $l^{dec}$ to the trail. When we deduce the value for $l$ using unit propagation on a clause $c$ we add $l^c$ to the trail. In our example search from above, the trail will be $\lnot x_1^{dec}, \lnot x_2^{dec}, \lnot x_3^{dec}, x_4^{(x_1\lor x_4)}$.

We also need to save the current `decision level` - the number of guessed values in the trail, and for each variable the decision level at which it was given value.

<!-- In fact, all of this can be viewed as one `implication graph`. Each node in the graph is a literal and when a literal value was understood from a clause there is an edge from the other variables in the clause to that literal. Each node also includes the decision level at which this literal was given value. -->

Consider the formula $$ (\lnot x_1 \lor \lnot x_2 \lor \lnot x_6)\land (\lnot x_1 \lor x_3)\land (\lnot x_3 \lor \lnot x_4)\land (x_2 \lor x_4 \lor x_5)\land (x_2 \lor \lnot x_5)\land (x_6)$$ A possible trail here is $$x_6^{(x_6)}, x_1^{dec}, \lnot x_2^{(\lnot x_1 \lor \lnot x_2 \lor \lnot x_6)}, x_3^{(\lnot x_1 \lor x_3)}, \lnot x_4^{(\lnot x_3 \lor \lnot x_4)}, x_5^{(x_2 \lor x_4 \lor x_5)}$$
<!-- and the corresponding implication graph is: -->

<!-- <div class="image-container">
    <img src="/unordered/09-sat/images/implication_graph1.png" width="671" height="331">
</div> -->

After that trail we reach a conflict at $(x_2\lor \lnot x_5)$.
<!-- <div class="image-container">
    <img src="/unordered/09-sat/images/implication_graph2.png" width="741" height="331">
</div> -->

This conflict will obviously be solved if the clause $(x_2 \lor \lnot x_5)$ will be satisfied. This does not tell us anything meaningful but we can use our trail to enlighten our results. We can replace $\lnot x_5$ with $(x_2 \lor x_4)$ because our trail told us that $\lnot x_5\equiv x_4\lor x_2$. Similarly, we then replace $x_4$ with $\lnot x_3$, then $\lnot x_3$ with $\lnot x_1$, then $x_2$ with $\lnot x_6 \lor \lnot x_1$. Overall the learning process was: 
 $$(x_2\lor \lnot x_5)\rightarrow (x_2\lor x_4)\rightarrow (x_2\lor \lnot x_3)\rightarrow (x_2\lor \lnot x_1)\rightarrow (x_2\lor \lnot x_5)\rightarrow (\lnot x_6\lor \lnot x_1)$$
At this point we stop because the new clause contained only one variable that was given value in the current decision level. If we stopped earlier, this clause will have more than one unassigned varialbe after backjump so we wouldn't be able to use it to avoid the same mistake.

In our case we can actually ignore $x_6$ because it was inferred in decision level 0 so will never change giving us $(\lnot x_1)$. It just looks like we overcomplicated backtracking because our new clause basically says "the error was guessing $x_1$ as positive so assign it False", but conflict analyzing is usually much more informative.

Take a look at the following trail:
 $$ x_1^{dec}, \lnot x_2^{(\lnot x_1 \lor \lnot x_2)}, x_3^{(\lnot x_1 \lor x_3)}, x_4^{dec}, \lnot x_5^{(\lnot x_4 \lor \lnot x_5)}, x_6^{(x_2\lor x_5\lor x_6)}, x_7^{(x_5\lor x_7)} $$
and assume the conflict was $(\lnot x_6 \lor \lnot x_7)$. The clause learning proccess will be as follows:
 $$(\lnot x_6 \lor \lnot x_7)\rightarrow (\lnot x_6 \lor x_5)\rightarrow (x_2 \lor x_5)$$
Then, after backjumping before the decision of $x_4$ this clause will inform us (using unit propagation) to assign $x_5$ a positive value.

The logic was quite simple. Until the learned clause has only one literal from the current decision level, replace literals with the rest of the clause that gave them their value.

### Implementation
We will now implement the ideas above, starting with implementing our data structures. The trail will be saved in two different structures: the list 'trail' that just keeps the literals in the order they were given value, and the dictionary 'antecedents' that for each literal in the trail remembers the clause that gave it value (or None in case of decision). We also maintain the dictionary 'decided_at' that for each literal shows the decision level at which it was given value.
Here is that in code:
```python
assignment = {}
trail = []
antecedent = {}
decision_level = 0
decided_at = {}
```

Searching for a conflict means looping over all clauses and looking whether the assignment gives it a negative value. In 'unit_propagate' we already loop over every clause and literal so we now add the functionality of checking conflicts:

++
/\ Note that we now have to maintain the data structures.
```python
def unit_propagate_and_conflict():
    changed = True
    while changed:
        changed = False
        for clause in cnf:
            st, num_undef, last_undef = clause_status(clause, assignment)
            if st is True:
                continue
            if num_undef == 0:
                # found a conflict
                return clause
            if not last_undef:
                return None
            # if clause is unsatisfied with one unassigned
            if num_undef == 1:
                v = abs(last_undef)
                sign = last_undef > 0
                assignment[v] = sign
                antecedent[v] = clause
                trail.append(last_undef)
                decided_at[v] = decision_level
                changed = True
    return None
```
++

After finding a conflict we need to analyze it. Until the learned clause has one literal from the current decision level, we choose the last literal from the trail that appears in our clause, and replace it with its antecedent clause.

In the search we know that literals in the trail will be opposite to the literals in the learned clause (if the trail has -17 the learned clause should have 17). That is because the trail lead us to a conflict and the learned clause remembers that and shows us what to do instead.
```python
def analyze(conflict):
    learned = set(conflict)
    
    def count_level(clause):
        count = 0
        for lit in clause:
            if decided_at[abs(lit)] == decision_level:
                count += 1
        return count
    
    while count_level(learned) > 1:
        # get the last literal on the trail that appears in the clause
        next_lit = next(l for l in reversed(trail) if -l in learned)

        ant = antecedent[abs(next_lit)]

        learned = learned.union(set(ant)) - {next_lit, -next_lit}

    cnf.append(list(learned))
```

Backjumping to a previous decision level simply means popping elements from the trail until we reach literals from that decision level.

```python
def backjump(level):
    var = abs(trail[-1])
    while decided_at[var] > level:
        del assignment[var]
        trail.pop()
        if not trail:
            break
        var = abs(trail[-1])
```

Now for the main loop of the algorithm. We apply unit propagation as much as we can. If we encounter a conflict we analyze it to add a new clause, backjump, and return to the start. If no conflict is found we have to guess. We choose the next unassigned variable and assign it True (incrementing the decision level by 1). There is no need to remember it and assign it False after backtracking (unlike DPLL) because in CDCL backjumping comes with a new clause that will tell us what was the mistake.

```python
def solve(cnf):
    max_var = max(abs(l) for c in cnf for l in c)
    assignment = {}
    trail = []
    antecedent = {}
    decision_level = 0
    decided_at = {}
    
    def unit_propagate_and_conflict(): ...
    def analyze(conflict): ...
    def backjump(level): ...

    while True:
        conflict = unit_propagate_and_conflict()
        if conflict:
            if decision_level == 0:
                return False
            
            analyze(conflict)

            decision_level -= 1
            backjump(decision_level)

            continue

        if eval_cnf(cnf, assignment):
            return assignment.copy()
        
        next_var = next(v+1 for v in range(max_var) if v+1 not in assignment)
        assignment[next_var] = True
        decided_at[next_var] = decision_level
        antecedent[next_var] = None
        trail.append(next_var)
        decision_level += 1
```