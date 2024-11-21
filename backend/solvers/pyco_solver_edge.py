from collections import defaultdict

from tqdm import tqdm
import pycosat

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

    def x(self, edge1, index, edge2=None):
        """
        Maps an edge and path index to a unique variable
        """
        if edge1 == edge2:
            raise ValueError("edge1 and edge2 must be different edges")

        def edge_to_num(edge):
            v, w = edge
            x1, y1 = v
            x2, y2 = w
            return x1 * self.n**3 + y1 * self.n**2 + x2 * self.n + y2

        num_paths = self.num_paths
        num1 = edge_to_num(edge1)
        num2 = edge_to_num(edge2) + 1 if edge2 is not None else 0
        return (num2 * self.n**4 + num1) * num_paths + index + 1

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
        edge2 = None
        if rest != 0:
            rest -= 1
            rest, y2 = divmod(rest, n)
            rest, x2 = divmod(rest, n)
            x1, y1 = divmod(rest, n)
            edge2 = ((x1, y1), (x2, y2))

        return edge1, index, edge2

    def edge_squared_constraints(self):
        # make sure that the (edge1, edge2) is true if and only if (edge1) and (edge2) are true
        clauses = []
        for index in range(self.num_paths):
            for edge1 in self.edges:
                for edge2 in self.edges:
                    if edge1 != edge2:
                        var1 = self.x(edge1, index)
                        var2 = self.x(edge2, index)
                        var3 = self.x(edge1, index, edge2)
                        clauses.append([-var1, -var2, var3])
                        clauses.append([var1, -var3])
                        clauses.append([var2, -var3])
        return clauses

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
            literals = [
                self.x(e, i)
                for e in self.vertex_to_edges[v]
                for i in range(self.num_paths)
            ]
            clauses += at_least_one(literals)

            # Require at least two edges per vertex for each path
            for index in range(self.num_paths):
                literals = [self.x(e, index) for e in self.vertex_to_edges[v]]
                clause = at_least_one(literals)[0]
                for literal in literals:
                    clause_copy = clause.copy()
                    clause_copy.remove(literal)
                    clause_copy.append(
                        -literal
                    )  # If literal is True, one of the others must be True
                    clauses.append(clause_copy)

            # but also can't be the case that there's more than 2 edges
            # all edges across all paths
            literals = [
                self.x(e1, i, e2)
                for e1 in self.vertex_to_edges[v]
                for i in range(self.num_paths)
                for e2 in self.vertex_to_edges[v]
                if e1 < e2
            ]
            clauses += at_most_one(literals)

        return clauses

    def solve(self):
        # verify that x and inverse_x are inverses
        # for edge in self.edges:
        #     for index in range(self.num_paths):
        #         assert self.inverse_x(self.x(edge, index)) == (edge, index, None)
        #         for edge2 in self.edges:
        #             if edge != edge2:
        #                 assert self.inverse_x(self.x(edge, index, edge2)) == (
        #                     edge,
        #                     index,
        #                     edge2,
        #                 )

        clauses = []
        clauses += self.at_most_one_path_per_edge()
        clauses += self.exactly_one_edge_per_vertex_on_path()
        clauses += self.exactly_two_edges_per_vertex_not_in_pair()
        clauses += self.edge_squared_constraints()

        for _ in tqdm(range(50)):
            literals = pycosat.solve(clauses)

            if literals == "UNSAT":
                return None

            solution = [[0 for _ in range(self.n)] for _ in range(self.n)]
            for literal in literals:
                if literal > 0:
                    edge, index, edge2 = self.inverse_x(literal)
                    if edge2 is not None:
                        continue

                    for x, y in edge:
                        if solution[x][y] != 0 and solution[x][y] != index + 1:
                            print("HUHH")
                            print(x, y)
                            print(solution[x][y], index + 1)
                            continue
                        solution[x][y] = index + 1

            # TODO: Fix this
            if not contains_cycle(solution):
                return solution

            clauses.insert(0, [-l for l in literals])
            print(len(clauses))
            # clauses.append([-l for l in literals])

        print("WTF")
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


def contains_cycle(puzzle):
    n = len(puzzle)
    visited = [[False] * n for _ in range(n)]

    def dfs(x, y, parent):
        if visited[x][y]:
            return True
        visited[x][y] = True

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < n
                and 0 <= ny < n
                and puzzle[nx][ny] != 0
                and (nx, ny) != parent
            ):
                if dfs(nx, ny, (x, y)):
                    return True
        return False

    for x in range(n):
        for y in range(n):
            if puzzle[x][y] != 0 and not visited[x][y]:
                if dfs(x, y, None):
                    return True
    return False


# Test the solver
if __name__ == "__main__":
    puzzle = [
        [0, 0, 1, 2, 0],
        [0, 4, 0, 0, 0],
        [0, 0, 2, 0, 0],
        [0, 0, 4, 0, 0],
        [1, 0, 0, 0, 0],
    ]

    puzzle = [
        [0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0],
        [3, 0, 3, 0, 0],
        [0, 0, 2, 0, 0],
        [0, 0, 0, 0, 2],
    ]

    solver = PycoEdgeSolver(puzzle)
    solution = solver.solve()
    # print puzzle
    print("Puzzle:")
    for row in puzzle:
        print(row)
    print()
    # print solution
    print("Solution:")
    if solution is None:
        print("No solution found")
    else:
        for row in solution:
            print(row)
