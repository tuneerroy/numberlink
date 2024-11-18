import random
from collections import defaultdict

Puzzle = list[list[int]]


def generate_board(grid_size: int) -> tuple[Puzzle, Puzzle]:
    puzzle = create_dominos(int(grid_size))
    shuffle_dominos(puzzle)

    best_puzzle = None
    best_num_dominos = float("inf")
    for _ in range(10000):
        puzzle, num_dominos = dominos_to_puzzle(puzzle)
        if num_dominos < best_num_dominos:
            best_num_dominos = num_dominos
            best_puzzle = puzzle

    empty_puzzle = remove_solution(best_puzzle)

    return empty_puzzle, best_puzzle


def remove_solution(puzzle: Puzzle) -> Puzzle:
    # need to find the dominos that have num neighbors = 1
    def get_neighbors(x, y):
        return [
            (x + dx, y + dy)
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
            if 0 <= x + dx < len(puzzle) and 0 <= y + dy < len(puzzle)
        ]

    def get_degree(x, y):
        return sum(puzzle[x][y] == puzzle[nx][ny] for nx, ny in get_neighbors(x, y))

    return [
        [puzzle[x][y] if get_degree(x, y) == 1 else 0 for y in range(len(puzzle))]
        for x in range(len(puzzle))
    ]


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
    # make bottom right cell connect
    dominos[-1][-1] = dominos[-1][-2]

    def get_neighbors(x, y):
        return [
            (x + dx, y + dy)
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
            if 0 <= x + dx < len(dominos) and 0 <= y + dy < len(dominos)
        ]

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
        x = find(x)
        y = find(y)
        parents[x] = y

    def get_degree(neighbors, value):
        return sum(find(dominos[x][y]) == value for x, y in neighbors)

    def is_cycle(x, y, allowed_values):
        color = defaultdict(int)

        def dfs(x, y, parent):
            if color[(x, y)] == 1:
                return True
            color[(x, y)] = 1
            for nx, ny in get_neighbors(x, y):
                if (nx, ny) == parent:
                    continue
                if find(dominos[nx][ny]) not in allowed_values:
                    continue
                if dfs(nx, ny, (x, y)):
                    return True
            color[(x, y)] = 2
            return False

        return dfs(x, y, None)

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
                # edge node
                if get_degree(get_neighbors(nx, ny), find(dominos[nx][ny])) < 2:
                    # need to also check that this doesn't create a cycle, how do we check?
                    # dfs search
                    if is_cycle(x, y, (find(dominos[x][y]), find(dominos[nx][ny]))):
                        continue
                    # we can just make keep track of all neighboring nodes of ALL nodes in the current parent
                    union(dominos[x][y], dominos[nx][ny])
                    break

    # reindex the dominos
    remaining_parents = [i for i in range(1, max_num + 1) if find(i) == i]
    parent_to_reindex = {parent: i + 1 for i, parent in enumerate(remaining_parents)}

    # TODO: need to check the final bottom right cell
    return [[parent_to_reindex[find(d)] for d in row] for row in dominos], len(
        remaining_parents
    )
