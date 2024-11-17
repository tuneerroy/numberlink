import pycosat
from collections import defaultdict

Puzzle = list[list[int]]

class PycoEdgeSolver:
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

        edges = []
        vertex_to_edges = defaultdict(list)
        for x in range(n):
            for y in range(n):
                if x + 1 < n:
                    edges.append(((x, y), (x + 1, y)))
                    vertex_to_edges[(x, y)].append(((x, y), (x + 1, y)))
                    vertex_to_edges[(x + 1, y)].append(((x, y), (x + 1, y)))
                if y + 1 < n:
                    edges.append(((x, y), (x, y + 1)))
                    vertex_to_edges[(x, y)].append(((x, y), (x, y + 1)))
                    vertex_to_edges[(x, y + 1)].append(((x, y), (x, y + 1)))

        self.edges = edges
        self.vertex_to_edges = vertex_to_edges

    def x(self, edge, index):
        """
        Maps an edge and path index to a unique variable
        """
        def edge_to_num(edge):
            v, w = edge
            x1, y1 = v
            x2, y2 = w
            return x1 * self.n**3 + y1 * self.n**2 + x2 * self.n + y2

        num_paths = self.num_paths
        return edge_to_num(edge) * num_paths + index + 1

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
        x1, y1 = divmod(rest, n)

        return ((x1, y1), (x2, y2)), index

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
                for i in range(self.num_paths):
                    if i != index:
                        literals = [self.x(e, i) for e in self.vertex_to_edges[v]]
                        clauses += none(literals)
        return clauses

    def exactly_two_edges_per_vertex_not_in_pair(self):
        clauses = []
        pair_vertices = {v for pair in self.pairs for v in pair}
        for v in self.vertices:
            if v in pair_vertices:
                continue

            # Require at least one edge across all paths
            literals = [self.x(e, i) for e in self.vertex_to_edges[v] for i in range(self.num_paths)]
            clauses += at_least_one(literals)

            # Require at least two edges per vertex for each path
            for index in range(self.num_paths):
                literals = [self.x(e, index) for e in self.vertex_to_edges[v]]
                clause = at_least_one(literals)[0]
                for literal in literals:
                    clause_copy = clause.copy()
                    clause_copy.remove(literal)
                    clause_copy.append(-literal)  # If literal is True, one of the others must be True
                    clauses.append(clause_copy)

        return clauses

    def solve(self):
        clauses = []
        clauses += self.at_most_one_path_per_edge()
        clauses += self.exactly_one_edge_per_vertex_on_path()
        clauses += self.exactly_two_edges_per_vertex_not_in_pair()

        literals = pycosat.solve(clauses)

        if literals == "UNSAT":
            return None

        solution = [[0 for _ in range(self.n)] for _ in range(self.n)]
        for literal in literals:
            if literal > 0:
                edge, index = self.inverse_x(literal)
                x1, y1 = edge[0]
                x2, y2 = edge[1]
                solution[x1][y1] = index + 1
                solution[x2][y2] = index + 1
        return solution


# HELPER METHODS
def at_least_one(literals):
    return [literals]

def none(literals):
    return [[-literal] for literal in literals]

def at_most_one(literals):
    return [[-l1, -l2] for l1 in literals for l2 in literals if l1 < l2]

def exactly_one(literals):
    return at_least_one(literals) + at_most_one(literals)


# Test the solver
if __name__ == "__main__":
    puzzle = [
        [1, 0, 1],
        [2, 0, 2],
        [3, 0, 3]
    ]

    solver = NumberLinkSolver(puzzle)
    solution = solver.solve()
    print(solution)  # Expected output: [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
