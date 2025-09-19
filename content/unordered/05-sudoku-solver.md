---
title: "sudoku solver in python"
tags: ['cs', 'project', 'state-space', 'ai', 'python']
---

# building a sudoku solver in python

## backtracking

lets look at a sudoku board which i got from [project euler](https://projecteuler.net/problem=96)

++
/\ notice that sudoku's may have multiple correct answers given a specific starting state, the one in the image has only one solution
<div style="text-align: center">
    <div class="image-container">
        <img src="/files/sudoku.png" alt="sudoku" width="500" height="500">
        <label class="image-caption">a common sudoku with zeroes on unfilled cells  - locally sourced   </label>
    </div>
</div>
++

as you can see sudoku boards have numbers from $[9]$ for filled squares, and $0$ for squares that havent been given a value. $^{1}$ the idea is to fill the zeroes with values from $[9]$, such that;

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
                    ans, res = solve(sudoku_copy)
                    if ans == 1:  # check if value worked
                        return res
                    # if it wasnt a valid sudoku try something else.
    if zero_count == 0:
        return check_valid(sudoku), sudoku
```

in the worst case the runtime is $O(9^{81-k})$ where $k$ is the inital number of filled cells.

notice that this code is very inefficient, because we could for each cell only try values 
that are not duplicates of its `neighbors`,$^{2}$ and save $1$ recursion depth.
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

++
/\ note that `propagate` now replaces `check_valid`, because the sudoku turns from `valid` to `invalid` iff a value was updated to a "bad one".
```python
from copy import deepcopy

sudoku = [[{1,2,4,5,6,..} {1,2,..}, {1,2,..}, {1,3,4,5,..}, ...], [{1,2,..}, {1,2,..}, {1,2,..}, {2,3,4,5,..}, ...], ...]

# returns 0 if the sudoku has no solution, 1 otherwise.
def propagate(sudoku, i, j, val):
    for k in range(9):  # go through neighbor's in row
        if i != k and val in sudoku[i][k]:
            sudoku[i][k].remove(val)
        if len(sudoku[i][k]) == 0:
            return 0

    for k in range(9):  # go through neighbor's in row
        if j != k and val in sudoku[k][j]:
            sudoku[k][j].remove(val)
        if len(sudoku[k][j]) == 0:
            return 0

    block_i = i // 3
    block_j = j // 3

    for k in range(3):
        for l in range(3):
            iter_i = block_i * 3 + k
            iter_j = block_j * 3 + l

            if (iter_i != i or iter_j != j) and val in sudoku[iter_i][iter_j]:
                sudoku[iter_i][iter_j].remove(val)
            if len(sudoku[iter_i][iter_j]) == 0:
                return 0

    return 1  # arrays are passed by reference so no need to 'return sudoku'


def solve(sudoku):
    all_filled = 1
    for i in range(9):
        for j in range(9):
            if len(sudoku[i][j]) > 1:
                all_filled = 0
                for val in sudoku[i][j]:
                    sudoku_copy = deepcopy(sudoku)
                    sudoku_copy[i][j] = {val}

                    if (
                        propagate(sudoku_copy, i, j, val) == 0
                    ):  # sudoku_copy is not satisfiable
                        continue  # try other values for i,j

                    ans, res = solve(sudoku_copy)
                    if ans == 1:  # check if value worked
                        return ans, res

                return 0, sudoku  # no value for i,j gives a solution, so no solution.

    if all_filled == 1:
        return (
            1,
            sudoku,
        )  # if every dict in 'sudoku' is a singleton then its a correct answer.
```
++

the algorithm is based on two facts;
1. if the sudoku is completely filled, meaning all dictionaries are singletons. it is a solution for the original sudoku because of the correctness of `propagate`.
2. if the sudoku has atleast $1$ cell that has a couple possible values.
    a. propagation rules out solutions that are trivially bad.
    b. if there is no value for the cell that is part of a solution, then there is no solution.
    
the algorithm is very simple, in sudoku each cell needs to have a value.
so we pick one cell, guess a value for it from the cell's dictionary. 
and make as much work as possible without recursion, which will save us from wasting time on trivially bad sudokus.

notice that the algorithm picks its cell by scanning the sudoku `row-major`-wise.
that cell could have lots of possible values, and waste time doing heavy recursions on bad values,
thus by choosing the cell with least possible values but more than one value, we can cut a lot of runtime.

lets write that 

```python
def mrv(sudoku):

    min_size = 9  # start with the maximum possible dict size
    min_i, min_j = -1, -1
    fully_filled = 1

    for i in range(9):
        for j in range(9):
            if min_size > len(sudoku[i][j]) and len(sudoku[i][j]) > 1:
                fully_filled = 0
                min_size = len(sudoku[i][j])
                min_i = i
                min_j = j

    if fully_filled == 1:
        return -1, -1  # i could just return 'min_i, min_j' but we like simplicity

    return min_i, min_j


def solve(sudoku):

    i, j = mrv(sudoku)

    if i == -1 and j == -1:  # (-1,-1) is the return for a fully filled sudoku
        return (
            1,
            sudoku,
        )  # if every dict in 'sudoku' is a singleton then its a correct answer.

    for val in sudoku[i][j]:
        sudoku_copy = deepcopy(sudoku)
        sudoku_copy[i][j] = {val}

        if propagate(sudoku_copy, i, j, val) == 0:  # sudoku_copy is not satisfiable
            continue  # try other values for i,j

        ans, res = solve(sudoku_copy)
        if ans == 1:  # check if value worked
            return ans, res

    return 0, sudoku  # no value for i,j gives a solution, so no solution.
```

we managed to write an efficient `CSP` algorithm, now we will make it even faster by switching
to another data structure called the `dancing links` to solve the exact cover problem.

## dancing links

### what is the exact cover problem?

given a collection $S$ of subsets of the set $X$, an exact cover of $X$ by the collection $S$, 
is a subcollection $S^*$ of $S$ such that every element in $X$ is contained in exactly one subset in $S^*$

or in other words, given a collection $S$ of subsets of the set $X$, an exact cover of $X$ by the collection $S$, 
such that;
1. the intersection of any two elements of $S^*$ is empty
2. the union of all elements in $S^*$ is equal $X$

lets say we have the exact cover problem, meaning we have $S, X$ and want to find $S^*$.<br>
we could represent the input as a binary matrix where each column is an element in $X$
and every row is an element of $S$ meaning a subset of $X$, where there is a $1$ in a column
if that element in $X$ is present in the subset.

for example, for $X=\{1,2,3\}, S=\{\{1,3\}, \{2,3\}, \{3\}\}$
the matrix would be 

$$
\begin{bmatrix}
    1 & 0 & 1 \\
    0 & 1 & 1 \\
    0 & 0 & 1 \\
\end{bmatrix}
$$

now, given the matrix we will solve for $S^*$ with the following algortihm

## knuth's algorithm X


the algorithm goes as follows, given a matrix $A$
1. if the matrix $A$ has no columns, the current partial solution is a valid solution; <br> 
   terminate successfully
2. otherwise, choose a column $c$ deterministically (with mrv for example)
3. for each row $r$ such that $A_{r,c}=1$
4. for each column $j$ such that $A_{r,j}=1$: <br>
        a. for each row $i$ such that $A_{i,j}=1$, delete row $i$ from matrix $A$ <br>
        b. delete column $j$ from matrix $A$ <br>
5. backtrack on step 3 if we haven't found a solution

to create a perfect cover we need two things, that each two rows in the solution have no intersection 
and all the rows in the solution fill all the columns, we accomplish the first in step $(4.a)$, and the second in $(1)$.
its extremely similar to the `constraint propagation` we wrote before.

thing is that generating matrices with less rows/columns is very expensive, the overhead from creating matrices would kill the algorithm.
thus instead we are going to represent the matrices as `sparse matrices` that will have easy removal of rows, and columns. to do so we are going to use doubly linked lists, to implement `knuth's dancing links` data structure.

the `dancing links` data structure is made up of 2 main components:
1. a column header which is a horizontal a doubly linked list, for easy removal and tracking of columns.
2. each column header node has a doubly linked list going down, where each node represents a $1$ on the matrix $A$.

the doubly linked lists going down connect to eachother creating a lattice structure, such that each node has a `left`, `right`, `up`, `down`.
heres an image depicting the data structure

<div style="text-align: center">
    <div class="image-container">
        <img src="/files/dancing-links.png" alt="sudoku" width="500" height="500">
        <label class="image-caption">depiction of the datastructure - <a href="https://kychin.netlify.app/sudoku-blog/dlx/">nigel chin</a></label>
    </div>
</div>

let's say we have a binary matrix $A$ we want to create the `dancing links` from, lets start by defining the column-header-node object, and the node object, and then linking everything.

++
/\ note that `root` isn't an actual column header its only the beginning of the linked list 
/\ remember `new_node.index` for later, we will use it in the final `solve` function
/\ we create `row_map` to map each index (i,j,k) to the corresponding `first_node_in_row`
```python
class columnHeader:
    def __init__(self):
        self.size = 0
        self.left = self
        self.right = self
        self.up = self
        self.down = self

class node:
    def __init__(self, column_header=None):
        self.column = column_header
        self.left = self
        self.right = self
        self.up = self
        self.down = self

def create_structure (A):
    root = columnHeader()
    num_rows = len(A)
    num_cols = len(A[0])
    columns = []

    for i in range(num_cols):
        header = columnHeader()
        columns.append(header)

        header.right = root
        header.left = root.left
        root.left.right = header
        root.left = header

    row_map = {}

    for i in range(num_rows): # iterate rows
        first_node_in_row = None
        for j in range(num_cols): # iterate columns
            val = A[i][j]
            if val == 1:
                header = columns[j]
                new_node = node(header)

                # we insert new rows at the bottom
                new_node.up = header.up
                new_node.down = header
                new_node.up.down = new_node
                header.up = new_node

                new_node.index = i # remember this!
                new_node.column = header
                header.size += 1

                if first_node_in_row == None:
                    first_node_in_row = new_node
                else:
                    new_node.right = first_node_in_row
                    new_node.left = first_node_in_row.left
                    first_node_in_row.left.right = new_node 
                    first_node_in_row.left = new_node

        row = i // 81
        col = (i % 81) // 9
        val = (i % 9) + 1
        row_map[(row, col, val)] = first_node_in_row
    return root, row_map # return the first element of the column header
```
++

now we want to implement the "dancing" which is the easy removal of nodes and restoration of removed nodes.
the nodes we are going to remove / restore, are those mentioned in step 4 of the `algorithm X`.
where after choosing a row to be part of the final solution from a given column, we remove all other rows that cover that column. that is the `covering`
and the `uncovering` refers to undoing that step.

for the algorithm to work we need to make sure to call `uncover` right after doing the matching `cover`. 
but thats an inherent property of backtracking so no worries.

++
/\ `node.column.size` is to keep track of how many $1$ 's in a column for the `mrv` heuristic.
/\ <br><br> notice that we also iterate the other way around in `uncover` precisely retracing our steps.
```python
def cover (column_header):

    column_header.left.right = column_header.right
    column_header.right.left = column_header.left

    col_iter = column_header.down
    while col_iter != column_header: # we iterate down in col

        row_iter = col_iter.right
        while row_iter != col_iter: # we iterate right in row
            row_iter.down.up = row_iter.up
            row_iter.up.down = row_iter.down
            row_iter.column.size -= 1
            row_iter = row_iter.right
        col_iter = col_iter.down


def uncover (column_header):

    column_header.left.right = column_header
    column_header.right.left = column_header

    col_iter = column_header.up
    while col_iter != column_header: # we iterate 
    
        row_iter = col_iter.left
        while row_iter != col_iter:
            row_iter.down.up = row_iter
            row_iter.up.down = row_iter
            row_iter.column.size += 1
            row_iter = row_iter.left
        col_iter = col_iter.up

    return 0 
```
++

when we `cover` we are essentially removing a column and some rows tied to it, we remove the column from the column header list, and disconnect every tied row from its vertical neighbors. 
but we never actually delete the links of the column to the rows, or the links from each row node to its vertical neighbors.
so we can undo this operation quite easily by finding all the links going out of the column horizontally and relinking each vertically. 

<br> to model a sudoku as an `exact cover problem` we need to decide on $S, X$ such that the computed $S^*$ actually means something to us. let's decide on <br>
$$X=\{a_{i,j}\space |\space 0\leq i,j\leq 8, a_{i,j} \in {0,1}\} \cup \{b_{i,j}\space |\space 0\leq i,j\leq 8, b_{i,j} \in {0,1}\}$$ $$\cup\space \{c_{i,j}\space |\space 0\leq i,j\leq 8, c_{i,j} \in {0,1}\} \cup \{d_{i,j}\space |\space 0\leq i,j\leq 8, d_{i,j} \in {0,1}\}$$
++
/\ note that each rule here has $81$ possible values which is nice
where each element represents a "rule": <br>
1. $a_{i,j}$ is $1$ if the cell at position $(i,j)$ is filled <br>
2. $b_{i,j}$ is $1$ if $i$ th row has the number $j$ <br>
3. $c_{i,j}$ is $1$ if $i$ th column has the number $j$ <br>
4. $d_{i,j}$ is $1$ if $i$ th box has the number $j$ <br>
++

in code we will organize $X$ as an array that will contain elements in order:
 $$[a_{0,0},...,a_{8,8},b_{0,0},...,b_{8,8},...,c_{0,0},...,c_{8,8},d_{0,0},...,d_{8,8}]$$

then we define $S=\{a_{i,j,k}\space |\space 0\leq i,j\leq 8,\space k\in [9]\}$, where $a_{i,j,k}$ means that the cell at position $(i,j)$ has value $k$.

 and we will organize $S$ in order:
 $$[a_{0,0,1},a_{0,0,2},...,a_{0,0,9},a_{0,1,1},a_{0,1,2}...,a_{0,1,9},...,a_{0,8,1},...,a_{0,8,9},a_{1,0,1},...,a_{1,8,9},...,a_{8,8,9}]$$

then we define $A$ to binary matrix with $S$ as rows, and $X$ as columns. <br>
thus $|A|=|S|\times|X|=(9^3)\times(81\cdot 4)=729\times324$

the outputted $S^*$ will be an assortment of rows such that they have no intersection and together satisfy all the $324$ "rules". because each row represents a value for a cell, we can translate it to a solution for our intial sudoku.

<br> now into how we fill the matrix $A$. lets say we have a row that represents " the cell $(i,j)$ has value $k$ ", 
then we would lit up all $a_{i,j}\space b_{i,k}\space c_{j,k}\space d_{3 \cdot (\lfloor{\frac{i}{3}}\rfloor) + (\lfloor{\frac{j}{3}}\rfloor),\space k}$

++
/\ please think on the indices until you understand how they tie to the definition and order of $X$
/\ <br><br> note that each row has atleast one value, $4$ to be precise.
```python
def create_matrix():
    A = [[0 for i in range(324)] for j in range(729)]

    for i in range(729):
        # extract info from row index
        row = i // 81
        col = (i % 81) // 9
        val = i % 9 # notice val is from 0-8 for indexing
        box_index = 3 * (row // 3) + (col // 3) # box indices are in row-major, e.g. [b00, b01, b02, b10, b11, b12, b20, b21, b22]

        A[i][row * 9 + col] = 1
        A[i][81   + row * 9 + val] = 1
        A[i][2*81 + col * 9 + val] = 1
        A[i][3*81 + box_index * 9 + val] = 1 

    return A
```
++

notice that the matrix $A$ we mentioned, represents an `exact cover problem` that would have any legal sudoku as a solution.
if we are given an incomplete sudoku as input, the number of possible solutions would need to get cut drastically, to achieve that we need to do some pre-processing to the output from `create_structure(A)` before feeding it into `solve`.

lets say we are given an initial sudoku with some numbers and some blank spaces, to incorporate that into our skeleton we just need to remove the rows that are impossible.
for example, if the input incomplete-sudoku contains a $7$ on the cell $(1,2)$, we can remove all rows from $A$ that represent " the cell $(1,2)$ has value $i$ " for $i\neq 7$.

which is exactly the notion we learned from step $(4)$ in `algorithm X`, meaning if we `cover` the $4$ column "rules" that containing $7$ on the cell $(1,2)$ we'd make sure those columns will only be covered once, and all other rows of possible values for the cell will be removed because of $a_{i,j}$ being turned on in both.

so to preprocess the `dancing links` structure we do the following:

++
/\ hints is just a $9\times 9$ matrix initialized to zeroes, partially-filled with numbers in $[9]$ that are hints
```python
def preprocess_structure(hints):
    root, row_map = create_structure(create_matrix())

    for i in range(9):
        for j in range(9):

            if hints[i][j] != 0:
                first_node_in_row = row_map[(i, j, hints[i][j])]
                row_iter = first_node_in_row.right
                cover(first_node_in_row.column)
                while row_iter != first_node_in_row: # cover all columns of the row defined by "the cell (i,j) has value 'hint[i][j]'"
                    cover(row_iter.column) # the horizontal links don't get removed by 'cover' so it's fine
                    row_iter = row_iter.right
    return root
```
++

with all that done the only thing missing would be to generate the `dancing links` from the matrix $A$, and run `algorithm X`.

```python
def solve(root, solution_rows):
    # if the matrix 'A' has no columns, the current partial solution is a valid solution (1)
    if root.left == root:
        return True
    # otherwise, choose a column 'c' deterministically (with mrv for example) (2)
    min_col = None
    min_value = float('inf')
    col_header_iter = root.right
    while col_header_iter != root: # loop over current active columns, find col with minimum number of 1's for 'mrv'
        if col_header_iter.size < min_value:
            min_col = col_header_iter
            min_value = col_header_iter.size

    col_iter = min_col.down
    # for each row 'col_iter' such that 'A[r][c]=1' (3)
    # each column is necessary for a final solution, so we cover 'col_iter' now
    cover(min_col)
    while col_iter != min_col:
        # extract info from row index
        row = col_iter.index // 81
        col = (col_iter.index % 81) // 9
        val = (col_iter.index % 9) + 1
        
        # delete conficting rows, delete column (4.a, 4.b)
        row_iter = col_iter.right
        while row_iter != col_iter:
            cover(row_iter.column)
            row_iter = row_iter.right
        
        solution_rows.append(col_iter.index)
        ans = solve(root, solution_rows)
        if ans == True:
            return ans

        # backtrack (5)
        solution_rows.pop()

        row_iter = col_iter.left
        while row_iter != col_iter:
            uncover(row_iter.column)
            row_iter = row_iter.left

        col_iter = col_iter.down

    uncover(min_col) # because we are using the same structure when we recurse up
    # if no solution found then there is no solution
    return False

def parse_solution(solution_rows, hints):

    solution_matrix = [row[:] for row in hints] # copy the hints matrix

    for i in solution_rows:
        row = i // 81
        col = (i % 81) // 9
        val = (i % 9) + 1
        solution_matrix[row][col] = val
        
    return solution_matrix

root, row_map = preprocess_structure(hints)
parse_solution(solve(root, []), hints)
```

## other sudoku variants

lets say we have another sudoku variant, 

<div style="text-align: center">
    <div class="image-container">
        <img src="/files/killer-sudoku.png" alt="sudoku" width="500" height="500">
        <label class="image-caption">a more complicated sudoku that uses sums - <a href="https://en.wikipedia.org/wiki/Killer_sudoku">Wikipedia</a></label>
    </div>
</div>

this is the killer sudoku variant which is a more strict sudoku, on top of the $3$ normal sudoku rules there is an additional one being that each color must sum to its number.

surprisingly, with a bit of cleverness we can copy our own work and reuse the `dancing links` to solve the killer sudoku.

## sudoku as a SAT problem

we can model CSP problems using first order logic and use a SAT solver.


---
$^{1}: [9]=\{1,2,3,4,5,6,7,8,9\}$ <br>
$^{2}:$ `neighbors` refers to all the cells it affects (constraint-wise). 
