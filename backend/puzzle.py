from generators.generator_1 import generate_board_1
from generators.generator_2 import generate_board_2

Puzzle = list[list[int]]


def create_puzzle(grid_size: int) -> tuple[Puzzle, Puzzle]:
    return generate_board_1(grid_size)

def print_puzzle(puzzle: Puzzle):
    max_width = max(len(str(num)) for row in puzzle for num in row)
    for row in puzzle:
        print(" ".join(f"{num:>{max_width}}" for num in row))


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    grid_size = input("Enter the grid size: ") if not args else args[0]
    if not grid_size.isdigit():
        print("Invalid input. Please enter a valid number.")
        exit(1)
    grid_size = int(grid_size)
    if grid_size < 2:
        print("Grid size must be at least 2.")
        exit(1)

    puzzle = create_dominos(int(grid_size))

    print("Original puzzle:")
    print_puzzle(puzzle)

    print("\nShuffled puzzle:")
    shuffle_dominos(puzzle)
    print_puzzle(puzzle)

    print("\nFinal puzzle:")
    best_puzzle = None
    best_num_dominos = float("inf")
    for _ in range(10000):
        puzzle, num_dominos = dominos_to_puzzle(puzzle)
        if num_dominos < best_num_dominos:
            best_num_dominos = num_dominos
            best_puzzle = puzzle

    print_puzzle(puzzle)

    puzzle, solution = create_puzzle(grid_size)

    print("\nEmpty puzzle:")
    print_puzzle(puzzle)

    print("\nSolution:")
    print_puzzle(solution)
