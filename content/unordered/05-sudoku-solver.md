---
title: "sudoku solver in python"
tags: ['cs', 'project', 'state-space', 'ai', 'python']
---

# building a sudoku solver in python

## backtracking

lets look at a sudoku board which i got from [project euler](https://projecteuler.net/problem=96)

<img src="/files/image.png" width="500" height="500">

as you can see sudoku boards have numbers from $[9]$ for filled squares, and $0$ for squares that havent been given a value.$^{1}$ the idea is to fill the zeroes with values from $[9]$, such that;

1. in every row there is no duplicate number

2. in every column there is no duplicate number

3. in every aligned 3x3 box denoted by the bold lines, there is no duplicate number.

these are the constraints of the problem.

because there are the same amount of values in a box, row, and column. and there are also no duplicates. you can think of each as a permutation of $[9]$, all the values $[9]$ appear once.

im sure there are lot of ways of solving sudoku, but im pretty sure that at the end of the day it boils down to choosing values for the zeroes, and *backtracking* if some constraint was invalidated.

<blockquote>
from the Oxford dictionary:
backtracking - retrace one's steps.
</blockquote>

the simplest way of backtracking is literally as the dictionary says. 
we look at all the cells that need to be filled, and for each cell try all the values, and if we find some invalidated constraint, we can just `return` meaning we stop exploring the branch. and if there are no `zero` cells, then we return whether its a valid sudoku solution.

lets write that,

```python
from copy import deepcopy

sudoku = [[3, 0, 0, 2, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 7, 0, 0, 0], ...]


def check_valid(sudoku):
    for i in range(9):
        values_seen = []
        for j in range(9):  # going through each row's values
            if sudoku[i][j] == 0:
                continue  # we don't care for 0 values
            if sudoku[i][j] in values_seen:
                return 0  # dupe found
            values_seen.append(sudoku[i][j])

    for j in range(9):
        values_seen = []
        for i in range(9):  # going through each col's values
            if sudoku[i][j] == 0:
                continue  # we don't care for 0 values
            if sudoku[i][j] in values_seen:
                return 0  # dupe found
            values_seen.append(sudoku[i][j])

    for i in range(3):
        for j in range(3):  # going through each block
            values_seen = []
            for k in range(3):
                for l in range(3):
                    index_r = 3 * i + k
                    index_c = 3 * j + l

                    if sudoku[index_r][index_c] == 0:
                        continue
                    if sudoku[index_r][index_c] in values_seen:
                        return 0
                    values_seen.append(sudoku[index_r][index_c])
    return 1


def solve(sudoku):
    zero_count = 0
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == 0:
                zero_count += 1
                for val in range(9):
                    sudoku_copy = deepcopy(sudoku)
                    sudoku_copy[i][j] = val
                    if solve(sudoku_copy) == 1:  # check if value worked
                        return sudoku_copy
                    # if it wasnt a valid sudoku try something else.
    if zero_count == 0:
        return check_valid(sudoku)
```

in the worst case the runtime is $O(9^{81-k})$ where $k$ is the inital number of filled cells.

notice that this code is very inefficient, because we could for each cell only try values 
that are not duplicates of its `neighbors`$^{2}$, and save $1$ recursion depth.
but why stop there? each time we set a value for a cell we could tell all it's `neighbors`
to not try that value, and if some cell has $0$ possible values then there is no solution.

thats exactly `constriant propagation`.

## constraint propagation

to start implementing `constraint propagation`, we need to detach from the 2d array of numbers 
we used and switch to a 2d array of sets. instead of the board holding the current values,
it will hold the possible values for each cell. such that if we want to try plotting a value in a cell,
we need to remove that value from all its `neighbors` sets.
and for each `neighbor` we check after the deletion if its size is zero, and if so there is no solution.

lets write that now,
```python

```

note that `propagate` now replaces `check_valid`, because the sudoku turns from `valid` to `invalid` iff a value was updated to a "bad one".
 

## dancing links


## sudoku as a SAT problem

---
$^{1}: [9]=\{1,2,3,4,5,6,7,8,9\}$ <br>
$^{2}:$ `neighbors` refers to all the cells it affects (constraint-wise). 
