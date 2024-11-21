import subprocess

import tqdm


def get_gen_output(width: int, height: int, n: int) -> str:
    path = __file__
    process_path = path.replace("generator_1.py", "numberlink/gen/gen.py")
    process = subprocess.run(
        [
            "python",
            process_path,
            str(width),
            str(height),
            str(n),
            "--zero",
            "--no-colors",
            "--terminal-only",
            "--solve",
            "--no-pipes",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        print(process.returncode)
        print(process.stdout)
        print(process.stderr)
        raise Exception("Error generating puzzles")
    return process.stdout


def parse_puzzle(grid: str) -> list[list[int]]:
    rows = grid.split("\n")[1:]  # skip first line (has dimensions)
    rows = [row.split() for row in rows]  # each val is space delimited
    return rows


def parse_solution(grid: str) -> list[list[int]]:
    rows = grid.split("\n")[1:]  # skip first line (has "Solution:")
    rows = [list(row) for row in rows]  # each val is a single char
    return rows


def parse_item(item: tuple[str, str]) -> tuple[list[list[int]], list[list[int]]]:
    puzzle = parse_puzzle(item[0])
    solution = parse_solution(item[1])
    # map each val to unique integer
    all_numbers = {num for row in puzzle for num in row}
    number_map = {num: i for i, num in enumerate(all_numbers, 1)}
    puzzle = [[number_map[num] if num != "0" else 0 for num in row] for row in puzzle]
    solution = [[number_map[num] for num in row] for row in solution]
    return puzzle, solution


def generate_grid(dimension, num_puzzles):
    output = get_gen_output(dimension, dimension, num_puzzles).strip()
    grids = output.split("\n\n")
    # every 2 grids is a puzzle & solution
    items = [(grids[i], grids[i + 1]) for i in range(0, len(grids), 2)]
    return [parse_item(item) for item in items]


def generate_board(size: int) -> tuple[list[list[int], list[list[int]]]]:
    return generate_grid(size, 1)[0]


if __name__ == "__main__":
    NUM_PUZZLES = 10
    MIN_DIMENSION = 4
    MAX_DIMENSION = 11
    assert MIN_DIMENSION <= MAX_DIMENSION

    d = []
    printables = []
    for dimension in tqdm.tqdm(range(MIN_DIMENSION, MAX_DIMENSION + 1)):
        grids = generate_grid(dimension, NUM_PUZZLES)
        for puzzle, solution in grids:
            printables.append((puzzle, solution))

    for i, (puzzle, solution) in enumerate(printables):
        print(f"puzzle_{i} = {puzzle}")
        print(f"solution_{i} = {solution}")
        print()
