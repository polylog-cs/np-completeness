from pysat.formula import CNF
from pysat.solvers import Glucose3

# Helper function to get variable number
def var(i, j, k):
    return 81 * (i - 1) + 9 * (j - 1) + k

def encode_sudoku(puzzle):
    cnf = CNF()

    # Each cell contains exactly one number
    for i in range(1, 10):
        for j in range(1, 10):
            cnf.append([var(i, j, k) for k in range(1, 10)])
            for k in range(1, 10):
                for l in range(k + 1, 10):
                    cnf.append([-var(i, j, k), -var(i, j, l)])

    # Row constraints
    for i in range(1, 10):
        for k in range(1, 10):
            for j in range(1, 10):
                for l in range(j + 1, 10):
                    cnf.append([-var(i, j, k), -var(i, l, k)])

    # Column constraints
    for j in range(1, 10):
        for k in range(1, 10):
            for i in range(1, 10):
                for l in range(i + 1, 10):
                    cnf.append([-var(i, j, k), -var(l, j, k)])

    # 3x3 sub-grid constraints
    for k in range(1, 10):
        for a in range(0, 3):
            for b in range(0, 3):
                for i in range(1, 4):
                    for j in range(1, 4):
                        for i2 in range(i + 1, 4):
                            for j2 in range(1, 4):
                                cnf.append([-var(3*a+i, 3*b+j, k), -var(3*a+i2, 3*b+j2, k)])

    # Initial clues
    for i in range(9):
        for j in range(9):
            if puzzle[i][j] != 0:
                cnf.append([var(i + 1, j + 1, puzzle[i][j])])

    return cnf

def solve_sudoku(puzzle):
    cnf = encode_sudoku(puzzle)
    solver = Glucose3()
    solver.append_formula(cnf.clauses)
    
    if solver.solve():
        model = solver.get_model()
        solution = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(1, 10):
            for j in range(1, 10):
                for k in range(1, 10):
                    if model[var(i, j, k) - 1] > 0:
                        solution[i-1][j-1] = k
        return solution
    else:
        return None

def print_sudoku(puzzle):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - -")
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            print(puzzle[i][j], end=" ")
        print()

# Example usage
puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# harder puzzle
puzzle = [
    [0, 0, 5, 3, 0, 0, 0, 0, 0],
    [8, 0, 0, 0, 0, 0, 0, 2, 0],
    [0, 7, 0, 0, 1, 0, 5, 0, 0],
    [4, 0, 0, 0, 0, 5, 3, 0, 0],
    [0, 1, 0, 0, 7, 0, 0, 0, 6],
    [0, 0, 3, 2, 0, 0, 0, 8, 0],
    [6, 0, 0, 5, 0, 0, 0, 0, 9],
    [0, 0, 4, 0, 0, 0, 0, 3, 0],
    [0, 0, 0, 0, 0, 9, 7, 0, 0]
]

print("Input Sudoku:")
print_sudoku(puzzle)

solution = solve_sudoku(puzzle)

if solution:
    print("\nSolution:")
    print_sudoku(solution)
else:
    print("\nNo solution exists.")