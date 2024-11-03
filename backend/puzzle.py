Puzzle = list[list[int]]


def create_puzzle(grid_size: int) -> Puzzle:
    return [[i] + ([0] * (grid_size - 2)) + [i] for i in range(grid_size)]


def solve_puzzle(puzzle: Puzzle) -> Puzzle:
    # will fill in the puzzle with the solution
    ...


def is_unique(puzzle: Puzzle) -> bool:
    # check if the puzzle is unique
    # basically need to ensure that there is only ONE solution
    ...
