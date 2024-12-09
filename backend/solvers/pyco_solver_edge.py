import itertools
from collections import defaultdict
from copy import deepcopy

import pycosat
from tqdm import tqdm

Puzzle = list[list[int]]


class PycoEdgeSolver:
    def __init__(self, puzzle):
        # puzzle is a list of lists of integers where 0 is empty, and any other number is a vertex
        self.puzzle = deepcopy(puzzle)
        n = len(puzzle)
        pairs = []
        pair_matches = defaultdict(list)
        for x in range(n):
            for y in range(n):
                vertex = puzzle[x][y]
                if vertex != 0:
                    pair_matches[vertex].append((x, y))

        for key in sorted(pair_matches.keys()):
            assert len(pairs) == key - 1
            pairs.append(pair_matches[key])

        self.n = n
        self.pairs = pairs
        self.num_paths = len(pairs)
        self.vertices = [(x, y) for x in range(n) for y in range(n)]

        edges = []
        vertex_to_edges = defaultdict(list)
        for x in range(n):
            for y in range(n):
                if x + 1 < n:
                    edge = ((x, y), (x + 1, y))
                    edges.append(edge)
                    vertex_to_edges[(x, y)].append(edge)
                    vertex_to_edges[(x + 1, y)].append(edge)
                if y + 1 < n:
                    edge = ((x, y), (x, y + 1))
                    edges.append(edge)
                    vertex_to_edges[(x, y)].append(edge)
                    vertex_to_edges[(x, y + 1)].append(edge)

        self.edges = edges

        # make sure correct number of edges for a grid of n x n
        assert len(edges) == 2 * n * (n - 1)

        self.vertex_to_edges = vertex_to_edges

    def x(self, edge1, index):  # , edge2=None):
        """
        Maps an edge and path index to a unique variable
        """

        def edge_to_num(edge):
            v, w = edge
            if v >= w:
                raise ValueError("v must be less than w")
            x1, y1 = v
            x2, y2 = w
            return x1 * self.n**3 + y1 * self.n**2 + x2 * self.n + y2

        num_paths = self.num_paths
        num1 = edge_to_num(edge1)
        return num1 * num_paths + index + 1

    def inverse_x(self, var):
        """
        Maps a variable back to its edge and path index
        """
        n = self.n
        num_paths = self.num_paths

        var -= 1
        e, index = divmod(var, num_paths)
        rest, y2 = divmod(e, n)
        rest, x2 = divmod(rest, n)
        rest, y1 = divmod(rest, n)
        rest, x1 = divmod(rest, n)

        edge1 = ((x1, y1), (x2, y2))
        return edge1, index

    def at_most_one_path_per_edge(self):
        clauses = []
        for e in self.edges:
            literals = [self.x(e, i) for i in range(self.num_paths)]
            clauses += at_most_one(literals)
        return clauses

    def exactly_one_edge_per_vertex_on_path(self):
        clauses = []
        for index in range(self.num_paths):
            vertices = self.pairs[index]
            for v in vertices:
                literals = [self.x(e, index) for e in self.vertex_to_edges[v]]
                clauses += exactly_one(literals)

                # Don't allow these vertices to be on other paths
                literals = [
                    self.x(e, i)
                    for e in self.vertex_to_edges[v]
                    for i in range(self.num_paths)
                    if i != index
                ]
                clauses += none(literals)
        return clauses

    def exactly_two_edges_per_vertex_not_in_pair(self):
        clauses = []
        pair_vertices = {v for pair in self.pairs for v in pair}
        for v in self.vertices:
            if v in pair_vertices:
                continue

            # Require at least one edge across all paths
            literals = [
                self.x(e, i)
                for e in self.vertex_to_edges[v]
                for i in range(self.num_paths)
            ]
            clauses += at_least_one(literals)

            # Require at most two edges across all paths
            # for every 2 edges, then the third edge must be false
            for e1, e2, e3 in itertools.combinations(self.vertex_to_edges[v], 3):
                for i, j, k in itertools.product(range(self.num_paths), repeat=3):
                    var1 = self.x(e1, i)
                    var2 = self.x(e2, j)
                    var3 = self.x(e3, k)
                    clauses.append([-var1, -var2, -var3])

            # Require at least two edges per vertex for each path
            for index in range(self.num_paths):
                literals = [self.x(e, index) for e in self.vertex_to_edges[v]]
                for literal in literals:
                    clause_copy = literals.copy()
                    clause_copy.remove(literal)
                    clause_copy.append(
                        -literal
                    )  # If literal is True, one of the others must be True
                    clauses.append(clause_copy)

        return clauses

    def solve(self):
        clauses = []
        clauses += self.at_most_one_path_per_edge()
        clauses += self.exactly_one_edge_per_vertex_on_path()
        clauses += self.exactly_two_edges_per_vertex_not_in_pair()

        # while True:
        literals = pycosat.solve(clauses)

        if literals == "UNSAT":
            return None, None

        solution = [[0 for _ in range(self.n)] for _ in range(self.n)]
        edges_set = set(self.edges)

        for literal in literals:
            if literal > 0:
                edge, index = self.inverse_x(literal)

                if edge not in edges_set:
                    continue

                for x, y in edge:
                    solution[x][y] = index + 1

        return fix_cycles(self.puzzle, solution), len(clauses)


# HELPER METHODS
def at_least_one(literals):
    return [literals]


def none(literals):
    return [[-literal] for literal in literals]


def at_most_one(literals):
    return [[-l1, -l2] for l1 in literals for l2 in literals if l1 < l2]


def exactly_one(literals):
    return at_least_one(literals) + at_most_one(literals)


def fix_cycles(original_puzzle, solution):
    n = len(solution)
    visited = [[False for _ in range(n)] for _ in range(n)]

    def dfs(i, j, val):
        if i < 0 or j < 0 or i >= n or j >= n or visited[i][j] or solution[i][j] != val:
            return
        visited[i][j] = True
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            dfs(i + dx, j + dy, val)

    for i in range(n):
        for j in range(n):
            # we only start search from og puzzle vertex
            if not visited[i][j] and original_puzzle[i][j] != 0:
                dfs(i, j, solution[i][j])

    # visited[i][j] = False === isolated component that just needs neighbor value
    for i in range(n):
        for j in range(n):
            if visited[i][j]:
                continue
            if i > 0 and visited[i - 1][j]:
                solution[i][j] = solution[i - 1][j]
                visited[i][j] = True
            elif j > 0 and visited[i][j - 1]:
                solution[i][j] = solution[i][j - 1]
                visited[i][j] = True
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if visited[i][j]:
                continue
            if i < n - 1 and visited[i + 1][j]:
                solution[i][j] = solution[i + 1][j]
                visited[i][j] = True
            elif j < n - 1 and visited[i][j + 1]:
                solution[i][j] = solution[i][j + 1]
                visited[i][j] = True

    return solution
