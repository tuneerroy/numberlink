import pycosat
from collections import defaultdict

Puzzle = list[list[int]]

class PycoPathSolver:
    def __init__(self, puzzle):
        # puzzle is a list of lists of integers where 0 is empty, and any other number is a vertex
        n = len(puzzle)
        pairs = []
        pair_matches = defaultdict(list)
        for x in range(n):
            for y in range(n):
                vertex = puzzle[x][y]
                if vertex != 0:
                    pair_matches[vertex].append((x, y))

        for pair in pair_matches.values():
            pairs.append(pair)

        self.n = n
        self.pairs = pairs
        self.num_paths = len(pairs)
        self.vertices = [(x, y) for x in range(n) for y in range(n)]

    def x(self, vertex, index, position):
        """
        vertex being None means the phantom vertex
        """
        n = self.n  # number of rows and columns
        num_paths = self.num_paths  # number of paths

        if vertex is not None:
            x, y = vertex
            vertex_num = x * n + y + 1  # +1 because 0 is the phantom vertex
        else:
            vertex_num = 0

        # index is based on how many paths we have
        ans = vertex_num * num_paths * (n**2 + 1) + index * (n**2 + 1) + position
        # +1 because we start from 1
        return ans + 1

    def inverse_x(self, var):
        n = self.n
        num_paths = self.num_paths

        var -= 1

        rest, position = divmod(var, n**2 + 1)
        vertex_num, index = divmod(rest, num_paths)
        if vertex_num == 0:
            vertex = None
        else:
            vertex_num -= 1
            x = vertex_num // n
            y = vertex_num % n
            vertex = (x, y)

        return vertex, index, position

    def each_vertex_in_a_single_path(self):
        n = self.n
        num_paths = self.num_paths

        clauses = []
        for vertex in self.vertices:
            literals = [
                self.x(vertex, index, position)
                for index in range(num_paths)
                for position in range(n**2 + 1)
            ]
            clauses += exactly_one(literals)
        return clauses

    def each_position_in_a_single_vertex(self):
        n = self.n
        num_paths = self.num_paths

        clauses = []
        for index in range(num_paths):
            for position in range(n**2 + 1):
                literals = [self.x(vertex, index, position) for vertex in self.vertices] + [
                    self.x(None, index, position)
                ]
                clauses += exactly_one(literals)
        return clauses

    def path_finished(self):
        n = self.n
        num_paths = self.num_paths

        clauses = []
        for index in range(num_paths):
            for position in range(n**2):
                clauses.append(
                    [-self.x(None, index, position), self.x(None, index, position + 1)]
                )
        return clauses

    def consecutive_vertices_along_path(self):
        n = self.n
        num_paths = self.num_paths
        x = self.x

        clauses = []
        for index in range(num_paths):
            for position in range(n**2):
                for vertex1 in self.vertices:
                    for vertex2 in self.vertices:
                        if not is_neighbor(vertex1, vertex2):
                            clauses.append([-x(vertex1, index, position), -x(vertex2, index, position + 1)])
        return clauses

    def source_and_sink(self):
        n = self.n
        num_paths = self.num_paths
        pairs = self.pairs
        x = self.x

        clauses = []
        for index in range(num_paths):
            clauses.append([x(pairs[index][0], index, 0)])
            for position in range(n**2):
                clauses.append(
                    [-x(pairs[index][1], index, position), x(None, index, position + 1)]
                )
            literals = [x(pairs[index][1], index, position) for position in range(n**2)]
            clauses += exactly_one(literals)
        return clauses

    def solve(self):
        clauses = []
        clauses += self.each_vertex_in_a_single_path()
        clauses += self.each_position_in_a_single_vertex()
        clauses += self.path_finished()
        clauses += self.consecutive_vertices_along_path()
        clauses += self.source_and_sink()

        literals = pycosat.solve(clauses)

        if literals == "UNSAT":
            return None

        n = self.n
        solution = [[0 for _ in range(n)] for _ in range(n)]
        for literal in literals:
            if literal > 0:
                vertex, index, _ = self.inverse_x(literal)
                if vertex is None:
                    continue
                x, y = vertex
                if solution[x][y] != 0:
                    raise ValueError("Multiple paths in the same cell")
                solution[x][y] = index + 1

        return solution


# HELPER METHODS
def at_least_one(literals):
    return [literals]

def at_most_one(literals):
    return [[-l1, -l2] for l1 in literals for l2 in literals if l1 < l2]

def exactly_one(literals):
    return at_least_one(literals) + at_most_one(literals)

def is_neighbor(vertex1, vertex2):
    x1, y1 = vertex1
    x2, y2 = vertex2
    return abs(x1 - x2) + abs(y1 - y2) == 1
