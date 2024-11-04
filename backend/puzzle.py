import random

Puzzle = list[list[int]]


def create_dominos(grid_size: int) -> Puzzle:
    return [[i] + ([0] * (grid_size - 2)) + [i] for i in range(grid_size)]


def solve_puzzle(puzzle: Puzzle) -> None:
    # will fill in the puzzle with the solution
    ...


def is_unique(puzzle: Puzzle) -> bool:
    # check if the puzzle is unique
    # basically need to ensure that there is only ONE solution
    ...


def create_dominos(grid_size: int) -> Puzzle:
    puzzle = [[0] * grid_size for _ in range(grid_size)]
    c = 1
    for i in range(grid_size):
        for j in range(1, grid_size, 2):
            puzzle[i][j - 1] = puzzle[i][j] = c
            c += 1
    if grid_size % 2 == 1:
        for i in range(1, grid_size, 2):
            puzzle[i - 1][-1] = puzzle[i][-1] = c
            c += 1
    return puzzle


def shuffle_dominos(puzzle: Puzzle, iterations=-1) -> None:
    if iterations < 0:
        iterations = len(puzzle) ** 2
        iterations = random.randint(iterations, iterations * 2)

    for _ in range(iterations):
        # need to make sure that the dominos stick together
        # i.e.
        # [[1, 1, 2],
        #  [2, 2, 3]]
        # needs to maintain that the numbers x and y are always adjacent
        # if x = y
        x = random.randint(0, len(puzzle) - 2)
        y = random.randint(0, len(puzzle) - 2)
        # if [[x, x],
        #     [y, y]]
        # we make it
        # [[x, y],
        #  [x, y]]
        if (
            puzzle[x][y] == puzzle[x][y + 1]
            and puzzle[x + 1][y] == puzzle[x + 1][y + 1]
        ):
            puzzle[x][y + 1], puzzle[x + 1][y] = puzzle[x + 1][y], puzzle[x][y + 1]
        # if [[x, y],
        #     [x, y]]
        # we make it
        # [[x, x],
        #  [y, y]]
        elif (
            puzzle[x][y] == puzzle[x + 1][y]
            and puzzle[x][y + 1] == puzzle[x + 1][y + 1]
        ):
            puzzle[x + 1][y], puzzle[x][y + 1] = puzzle[x][y + 1], puzzle[x + 1][y]


def dominos_to_puzzle(dominos: Puzzle, connections: int = -1) -> Puzzle:
    if connections < 0:
        connections = len(dominos) ** 2
        connections = random.randint(connections, connections * 2)

    # use union find to get the dominos heart
    max_num = len(dominos) ** 2 // 2
    parents = list(range(max_num + 1))

    def find(x):
        if parents[x] != x:
            parents[x] = find(parents[x])
        return parents[x]

    def union(x, y):
        parents[find(x)] = find(y)

    def get_degree(neighbors, value):
        return sum(find(dominos[x][y]) == value for x, y in neighbors)

    def get_neighbors(x, y):
        return [
            (x + dx, y + dy)
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
            if 0 <= x + dx < len(dominos) and 0 <= y + dy < len(dominos)
        ]

    for _ in range(connections):
        # randomly connect the dominos
        x = random.randint(0, len(dominos) - 1)
        y = random.randint(0, len(dominos) - 1)

        # if it's an edge node, then we can MAYBE connect it to another domino
        neighbors = get_neighbors(x, y)
        if get_degree(neighbors, find(dominos[x][y])) < 2:
            # then we can connect it to another domino
            # shuffle the neighbors so we can connect to a random domino
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if get_degree(get_neighbors(nx, ny), find(dominos[nx][ny])) < 2:
                    union(dominos[x][y], dominos[nx][ny])
                    break
    remaining_parents = [i for i in range(max_num + 1) if find(i) == i]
    parent_to_reindex = {parent: i + 1 for i, parent in enumerate(remaining_parents)}
    return [[parent_to_reindex[find(d)] for d in row] for row in dominos]


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
    puzzle = dominos_to_puzzle(puzzle)
    print_puzzle(puzzle)
