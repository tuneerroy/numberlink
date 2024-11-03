from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

"""
Backend for Numberlink puzzle game

Supports basic routes with main solution/puzzle creation logic in separate files
"""

class Puzzle(BaseModel):
    ...

app = FastAPI()

@app.get("/puzzle/{puzzle_id}")
def get_puzzle(puzzle_id: int):
    ...

@app.get("/puzzles/{puzzle_id}/solution")
def get_solution(puzzle_id: int):
    ...

@app.post("/puzzle") # basically requesting a new puzzle
def create_puzzle(difficulty: str):
    # should probably make it an ENUM ranging from easy to hard
    ...

@app.post("/puzzle/{puzzle_id}/validate")
def validate_puzzle(puzzle_id: int, puzzle: Puzzle):
    ...

@app.get("/puzzle/{puzzle_id}/hint")
def get_hint(puzzle_id: int):
    ...