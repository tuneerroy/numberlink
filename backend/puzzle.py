from generators import generator_1, generator_2, generator_3

Puzzle = list[list[int]]

generators = [
    generator_1.generate_board,
    generator_2.generate_board,
    generator_3.generate_board,
]


def get_number_of_generators() -> int:
    return len(generators)


def create_puzzle(grid_size: int, generator: int) -> tuple[Puzzle, Puzzle]:
    return generators[generator](grid_size)


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

    puzzle = create_puzzle(grid_size)
    print_puzzle(puzzle)
