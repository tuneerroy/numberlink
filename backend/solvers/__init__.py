from .utils import solver
from .constraint_solver_path import ConstraintPathSolver
from .pyco_solver_path import PycoPathSolver
from .pyco_solver_edge import PycoEdgeSolver


@solver
def run_constraint_path_solver(puzzle):
    solver = ConstraintPathSolver(puzzle)
    return solver.solve()


@solver
def run_pyco_path_solver(puzzle):
    solver = PycoPathSolver(puzzle)
    return solver.solve()


@solver
def run_pyco_edge_solver(puzzle):
    solver = PycoEdgeSolver(puzzle)
    return solver.solve()


solvers = {
    "ConstraintPathSolver": run_constraint_path_solver,
    "PycoPathSolver": run_pyco_path_solver,
    "PycoEdgeSolver": run_pyco_edge_solver,
}


__all__ = [
    "solvers",
    "run_constraint_path_solver",
    "run_pyco_path_solver",
    "run_pyco_edge_solver",
]
