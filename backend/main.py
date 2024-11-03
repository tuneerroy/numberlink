from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

"""
Backend for Numberlink puzzle game

Supports basic routes with main solution/puzzle creation logic in separate files
"""

MIN_PUZZLE_SIZE = 4
MAX_PUZZLE_SIZE = 10

Puzzle = list[list[int]]


class PuzzleResponse(BaseModel):
    id: int
    puzzle: Puzzle


class Item(BaseModel):
    difficulty: int  # grid size?
    puzzle: Puzzle
    solution: Optional[Puzzle]


db: list[Item] = []

app = FastAPI()


def validate_puzzle_id(puzzle_id: int):
    if puzzle_id < 0 or puzzle_id >= len(db):
        raise HTTPException(status_code=404, detail="Item not found")
    return puzzle_id


async def solve_puzzle(puzzle_id: int):
    def solve(puzzle: Puzzle): ...

    if db[puzzle_id].solution is None:
        db[puzzle_id].solution = solve(db[puzzle_id].puzzle)
    return db[puzzle_id].solution


@app.get("/puzzle/{puzzle_id}")
def get_puzzle(puzzle_id: int = Depends(validate_puzzle_id)) -> Puzzle:
    return db[puzzle_id].puzzle


@app.get("/puzzles/{puzzle_id}/solution")
def get_solution(puzzle_id: int = Depends(validate_puzzle_id)) -> Puzzle:
    return db[puzzle_id].solution


@app.post("/puzzle")  # basically requesting a new puzzle
def create_puzzle(difficulty: int, background_tasks: BackgroundTasks) -> PuzzleResponse:
    # should probably make it an ENUM ranging from easy to hard
    if difficulty < MIN_PUZZLE_SIZE or difficulty > MAX_PUZZLE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Difficulty must be between {MIN_PUZZLE_SIZE} and {MAX_PUZZLE_SIZE}",
        )
    # TODO: create the bloody puzzle
    puzzle = [[i] + ([0] * (difficulty - 2)) + [i] for i in range(difficulty)]
    db.append(Item(difficulty=difficulty, puzzle=puzzle, solution=None))

    # eventually solve the puzzle
    background_tasks.add_task(solve_puzzle, len(db) - 1)

    return PuzzleResponse(id=len(db) - 1, puzzle=puzzle)


@app.post("/puzzle/{puzzle_id}/validate")
def validate_puzzle(
    puzzle: Puzzle,
    puzzle_id: int = Depends(validate_puzzle_id),
):
    solution = db[puzzle_id].solution
    if solution is None:
        # solve right now and return
        solution = solve_puzzle(puzzle_id)
    if puzzle == solution:
        return {"message": "Puzzle is correct", "correct": True}
    return {"message": "Puzzle is incorrect", "correct": False}


@app.get("/puzzle/{puzzle_id}/hint")
def get_hint(puzzle_id: int):
    # TODO: implement hint logic

    # TODO: first check if current puzzle is valid?

    # NOTE: not sure we actually want to do this?

    pass
