import json
import subprocess

import tqdm


def get_gen_output(arg1: int, arg2: int, arg3: int) -> str:
    process = subprocess.run(
        [
            "python",
            "numberlink/gen/gen.py",
            str(arg1),
            str(arg2),
            str(arg3),
            "--zero",
            "--no-colors",
            "--terminal-only",
        ],
        capture_output=True,
        text=True,
    )
    return process.stdout


def get_grids(output):
    def parse_grid(grid):
        # skip first line (has dimensions)
        grid = grid.split("\n")[1:]
        # split rows into lists of numbers
        grid = [row.split() for row in grid]
        # get range of numbers
        numbers = {num for row in grid for num in row}
        # map each number to a unique integer
        number_map = {num: i for i, num in enumerate(numbers, 1)}
        grid = [[number_map[num] if num != "0" else 0 for num in row] for row in grid]
        return grid

    grids = output.split("\n\n")
    return [parse_grid(grid) for grid in grids if grid]


def generate_grid(dimension, num_puzzles):
    output = get_gen_output(dimension, dimension, num_puzzles)
    grids = get_grids(output)
    return grids


if __name__ == "__main__":
    NUM_PUZZLES = 1000
    MIN_DIMENSION = 4
    MAX_DIMENSION = 11
    assert MIN_DIMENSION <= MAX_DIMENSION

    d = []
    for dimension in tqdm.tqdm(range(MIN_DIMENSION, MAX_DIMENSION + 1)):
        grids = generate_grid(dimension, NUM_PUZZLES)
        d.append({"dimension": dimension, "grids": grids})

    with open("puzzles.json", "w") as f:
        json.dump(d, f, indent=4)
