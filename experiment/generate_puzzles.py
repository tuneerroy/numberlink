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
        grid = grid.split("\n")[1:]
        grid = [row.split() for row in grid]
        # get range of numbers
        numbers = {num for row in grid for num in row}
        # map each number to a unique integer
        number_map = {num: i for i, num in enumerate(numbers, 1)}
        grid = [[number_map[num] if num != "0" else 0 for num in row] for row in grid]
        return grid

    grids = output.split("\n\n")
    return [parse_grid(grid) for grid in grids if grid]


if __name__ == "__main__":
    d = []
    for dimension in tqdm.tqdm(range(4, 12)):
        output = get_gen_output(dimension, dimension, 100)
        grids = get_grids(output)
        d.append({"dimension": dimension, "grids": grids})

    with open("puzzles.json", "w") as f:
        json.dump(d, f, indent=4)
