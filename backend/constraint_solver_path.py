import itertools
from ortools.sat.python import cp_model

Puzzle = list[list[int]]

class ConstraintPathSolver:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.model = cp_model.CpModel()
        self.n_rows = len(puzzle)
        self.n_cols = len(puzzle[0])
        
        self.pairs = {}
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if puzzle[i][j] != 0:
                    val = puzzle[i][j]
                    if val not in self.pairs:
                        self.pairs[val] = ((i, j), None)
                    else:
                        self.pairs[val] = (self.pairs[val][0], (i, j))
        
        self.vars = {}
        self.phantom_vars = {}
    
    def create_vars(self):
        max_path_length = self.n_rows * self.n_cols
        for val, _ in self.pairs.items():
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    for p in range(max_path_length):
                        self.vars[(i, j, val, p)] = self.model.NewBoolVar(f"x_{i}_{j}_{val}_{p}")
            for p in range(max_path_length):
                self.phantom_vars[(val, p)] = self.model.NewBoolVar(f"phantom_{val}_{p}")
        
    def add_constraints(self):

        # Each vertex is visited at most once (1)
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                occupied_positions = [self.vars[(i, j, val, p)]
                                      for val in self.pairs
                                      for p in range(self.n_rows * self.n_cols)]
                self.model.Add(sum(occupied_positions) == 1)
        
        for val, (start, end) in self.pairs.items():
            # Source is the start of the path (5)
            self.model.Add(self.vars[(start[0], start[1], val, 0)] == 1)

            # Sink appears in path (5)
            sink_options = [self.vars[(end[0], end[1], val, p)] for p in range(self.n_rows * self.n_cols)]
            self.model.Add(sum(sink_options) == 1)

            # Sink is followed by phantom (5)
            for p in range(1, self.n_rows * self.n_cols):
                self.model.AddImplication(self.vars[(end[0], end[1], val, p - 1)], self.phantom_vars[(val, p)])
            
            # Ensure continuity with intermediate variables (4)
            for p in range(1, self.n_rows * self.n_cols):
                for i in range(self.n_rows):
                    for j in range(self.n_cols):
                        current_var = self.vars[(i, j, val, p)]
                        neighbor_vars = [
                            self.vars[(i + di, j + dj, val, p - 1)]
                            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                            if 0 <= i + di < self.n_rows and 0 <= j + dj < self.n_cols
                        ]
                        self.model.Add(sum(neighbor_vars) == 1).OnlyEnforceIf(current_var)
            
            # Ensure path finishing (3)
            for p in range((self.n_rows * self.n_cols) - 1):
                self.model.AddImplication(self.phantom_vars[(val, p)], self.phantom_vars[(val, p + 1)])
            

            # Each position is visited at most once (2)
            for p in range(self.n_rows * self.n_cols):
                occupied_positions = [self.vars[(row, col, val, p)]
                                      for row in range(self.n_rows)
                                      for col in range(self.n_cols)]
                occupied_positions.append(self.phantom_vars[(val, p)])
                self.model.Add(sum(occupied_positions) == 1)



    
    def solve(self):
        self.create_vars()
        self.add_constraints()

        solver = cp_model.CpSolver()
        sol_res = solver.Solve(self.model)

        if sol_res == cp_model.OPTIMAL or sol_res == cp_model.FEASIBLE:
            solution = [[0 for _ in range(self.n_cols)] for _ in range(self.n_rows)]
            for number in self.pairs:
                for p in range(self.n_rows * self.n_cols):
                    for row in range(self.n_rows):
                        for col in range(self.n_cols):
                            if solver.Value(self.vars[(row, col, number, p)]) == 1:
                                solution[row][col] = number
            # for number, p, row, col, in itertools.product(self.pairs, range(self.n_rows * self.n_cols), range(self.n_rows), range(self.n_cols)):
            #     if solver.Value(self.phantom_vars[(number, p)]) == 1:
            #         solution[row][col] = number
            return solution
        else:
            return None