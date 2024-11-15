from collections import deque, defaultdict
from contextlib import asynccontextmanager
from constraint_solver_path import ConstraintPathSolver
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel
from puzzle import Puzzle, create_puzzle

from fastapi.middleware.cors import CORSMiddleware

"""
Backend for Numberlink puzzle game

Supports basic routes with main solution/puzzle creation logic in separate files
"""

MIN_PUZZLE_SIZE = 5
MAX_PUZZLE_SIZE = 10


class Item(BaseModel):
    puzzle: Puzzle
    solution: Puzzle


class DbEntry(BaseModel):
    items: deque[Item] = []
    actively_generating: bool = False
    buffer_size: int = 0


db: list[DbEntry] = [DbEntry() for _ in range(MIN_PUZZLE_SIZE, MAX_PUZZLE_SIZE + 1)]


async def fill_buffer(difficulty: int):
    db_index = difficulty - MIN_PUZZLE_SIZE
    db_entry = db[db_index]
    db_entry.actively_generating = True
    while len(db_entry.items) < db_entry.buffer_size:
        puzzle, solution = create_puzzle(grid_size=difficulty)
        db_entry.items.append(Item(puzzle=puzzle, solution=solution))
    db_entry.actively_generating = False


async def initialize_db():
    for i in range(MIN_PUZZLE_SIZE, MAX_PUZZLE_SIZE + 1):
        db_index = i - MIN_PUZZLE_SIZE
        db[db_index].actively_generating = True

    for difficulty in range(MIN_PUZZLE_SIZE, MAX_PUZZLE_SIZE + 1):
        await fill_buffer(difficulty)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize the db
    # NOTE: intentionally don't await?
    # await initialize_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/difficulty")
def get_difficulty() -> dict:
    return {"min": MIN_PUZZLE_SIZE, "max": MAX_PUZZLE_SIZE}


@app.get("/puzzle")
def get_puzzle(difficulty: int, background_tasks: BackgroundTasks) -> Item:
    if difficulty < MIN_PUZZLE_SIZE or difficulty > MAX_PUZZLE_SIZE:
        raise HTTPException(status_code=404, detail="Difficulty not supported")

    db_index = difficulty - MIN_PUZZLE_SIZE
    db_entry = db[db_index]
    if len(db_entry.items) == 0:
        db_entry.buffer_size += 1
        puzzle, solution = create_puzzle(grid_size=difficulty)
        return Item(puzzle=puzzle, solution=solution)

    item = db_entry.items.pop()
    if not db_entry.actively_generating:
        background_tasks.add_task(fill_buffer, difficulty)

    return item

@app.post("/solve")
def solve_puzzle(puzzle: Puzzle) -> Puzzle:
    # ensure that the puzzle is valid
    counts = defaultdict(int)
    for row in puzzle:
        for val in row:
            counts[val] += 1
    for val, count in counts.items():
        if val == 0:
            continue
        if count != 2:
            raise HTTPException(status_code=400, detail="Invalid puzzle")

    keys = sorted(counts.keys())

    # map to 0-(n-1)
    mapping = {val: i for i, val in enumerate(keys)}
    # and back
    reverse_mapping = {i: val for val, i in mapping.items()}

    puzzle = [[mapping[val] for val in row] for row in puzzle]
    soln = ConstraintPathSolver(puzzle)
    
    # TODO: do we have multiple solutions?
    best_puzzle = soln.solve()

    if best_puzzle is None:
        raise HTTPException(status_code=400, detail="No solution found")

    # map back to original values
    puzzle = [[reverse_mapping[val] for val in row] for row in best_puzzle]

    return puzzle