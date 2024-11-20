from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from puzzle import Puzzle, create_puzzle, get_number_of_generators
from solvers import solvers

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


# each row is a generator
# each column is a difficulty level
db: list[list[DbEntry]] = [
    [DbEntry() for _ in range(MIN_PUZZLE_SIZE, MAX_PUZZLE_SIZE + 1)]
    for _ in range(get_number_of_generators())
]


async def fill_buffer(difficulty: int, generator_id: int):
    db_index = difficulty - MIN_PUZZLE_SIZE
    db_entry = db[generator_id][db_index]
    db_entry.actively_generating = True
    while len(db_entry.items) < db_entry.buffer_size:
        puzzle, solution = create_puzzle(grid_size=difficulty, generator=generator_id)
        db_entry.items.append(Item(puzzle=puzzle, solution=solution))
    db_entry.actively_generating = False


async def initialize_db():
    for i in range(get_number_of_generators()):
        for i in range(MIN_PUZZLE_SIZE, MAX_PUZZLE_SIZE + 1):
            db_index = i - MIN_PUZZLE_SIZE
            db[i][db_index].actively_generating = True

    for generator_id in range(get_number_of_generators()):
        for difficulty in range(MIN_PUZZLE_SIZE, MAX_PUZZLE_SIZE + 1):
            await fill_buffer(difficulty, generator_id)


app = FastAPI()

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


@app.get("/puzzle/{generator_id}")
def get_puzzle(
    generator_id: int, difficulty: int, background_tasks: BackgroundTasks
) -> Item:
    if generator_id < 0 or generator_id >= get_number_of_generators():
        raise HTTPException(status_code=404, detail="Generator not found")
    if difficulty < MIN_PUZZLE_SIZE or difficulty > MAX_PUZZLE_SIZE:
        raise HTTPException(status_code=404, detail="Difficulty not supported")

    db_index = difficulty - MIN_PUZZLE_SIZE
    db_entry = db[generator_id][db_index]
    if len(db_entry.items) == 0:
        db_entry.buffer_size += 1
        puzzle, solution = create_puzzle(grid_size=difficulty, generator=generator_id)
        return Item(puzzle=puzzle, solution=solution)

    item = db_entry.items.pop()
    if not db_entry.actively_generating:
        background_tasks.add_task(fill_buffer, difficulty, generator_id)

    return item


@app.post("/solve/{solver_id}")
async def solve_puzzle(puzzle: Puzzle, solver_id: str) -> Puzzle:
    if solver_id not in solvers:
        raise HTTPException(
            status_code=404,
            detail="Solver not found, must be one of: " + ", ".join(solvers.keys()),
        )

    solver = solvers[solver_id]

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

    mapping = {val: i for i, val in enumerate(sorted(counts.keys()))}
    puzzle_cpy = [[mapping[val] for val in row] for row in puzzle]

    try:
        # Run the solver with a timeout
        best_puzzle = await asyncio.wait_for(asyncio.to_thread(solver, puzzle_cpy), timeout=30.0)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Solver timed out after 30 seconds")

    if best_puzzle is None:
        raise HTTPException(status_code=400, detail="No solution found")

    new_mapping = dict()
    for i in range(len(puzzle)):
        for j in range(len(puzzle[i])):
            if puzzle[i][j] != 0:
                new_mapping[best_puzzle[i][j]] = puzzle[i][j]
    for i in range(len(best_puzzle)):
        for j in range(len(best_puzzle[i])):
            best_puzzle[i][j] = new_mapping[best_puzzle[i][j]]

    return best_puzzle
