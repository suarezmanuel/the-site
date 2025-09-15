from copy import deepcopy

# sudoku = [[{1,2,4,5,6,..} {1,2,..}, {1,2,..}, {1,3,4,5,..}, ...], [{1,2,..}, {1,2,..}, {1,2,..}, {2,3,4,5,..}, ...], ...]


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

    block_i = i % 3
    block_j = j % 3

    for k in range(3):
        for l in range(3):
            iter_i = block_i * 3 + k
            iter_j = block_j * 3 + l

            if (iter_i != i or iter_j != j) and val in sudoku[iter_i][iter_j]:
                sudoku[iter_i][iter_j].remove(val)
            if len(sudoku[iter_i][iter_j]) == 0:
                return 0

    return 1  # arrays are passed by reference so no need to `return sudoku`


def solve(sudoku):
    all_filled = 1
    for i in range(9):
        for j in range(9):
            if len(sudoku[i][j]) > 1:
                all_filled = 0
                for val in sudoku[i][j]:
                    sudoku_copy = deepcopy(sudoku)
                    sudoku[i][j] = val
                    if solve(sudoku) == 1:  # check if value worked
                        return sudoku
                    sudoku = (
                        sudoku_copy  # if it wasnt a valid sudoku try something else.
                    )

    if zero_count == 0:
        return check_valid(sudoku)
