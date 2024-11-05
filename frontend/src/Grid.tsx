import React, { useEffect, useState } from 'react'

interface GridProps {
    difficulty: number
}

const intToColor = (num: number) => `hsl(${(num * 137.5) % 360}, 70%, 70%)`

// Grid should be an array of Cells
// Each Cell should have a value and be either a head node

interface Cell {
    value: number
    isHead: boolean
}

interface PuzzleResponse {
    puzzle: number[][]
    solution: number[][]
}

const Grid: React.FC<GridProps> = ({ difficulty }) => {
    // const [grid, setGrid] = useState(Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i * n + j + 1) % (n * n + 1))))
    // grid should just be filled with 0s by default
    // set to empty array of cells 
    const [grid, setGrid] = useState<Cell[][]>([])
    const [solution, setSolution] = useState<number[][]>([])
    const [dragValue, setDragValue] = useState<number | null>(null)
    const [puzzleSolved, setPuzzleSolved] = useState(false)
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
        // make a get request to the backend to get the grid
        setIsLoading(true)
        fetch(`http://localhost:8000/puzzle?difficulty=${difficulty}`)
            .then(res => res.json())
            .then((data: PuzzleResponse) => {
                setSolution(data.solution)
                setGrid(
                    data.puzzle.map((row: number[]) =>
                        row.map(value => ({
                            value,
                            isHead: value !== 0
                        }))
                    )
                )
            })
            .catch(err => console.error(err))
            .finally(() => setIsLoading(false))
    }, [difficulty])

    useEffect(() => {
        if (grid.length === 0) return
        const isSolved = grid.every((row, rowIndex) =>
            row.every((cell, colIndex) => {
                return cell.value === solution[rowIndex][colIndex]
            })
        )
        setPuzzleSolved(isSolved)
    }, [grid, solution])


    const handleMouseDown = (row: number, col: number) => {
        const cell = grid[row][col]
        // only if non-zero value
        if (cell) {
            setDragValue(cell.value)
        }
    }

    const handleMouseOver = (row: number, col: number) => {
        if (dragValue) {
            setGrid(prevGrid => {
                const newGrid = prevGrid.map(row => [...row])
                if (!newGrid[row][col].isHead) {
                    newGrid[row][col].value = dragValue
                }
                return newGrid
            })
        }
    }

    const handleMouseUp = () => {
        setDragValue(null)
    }

    if (isLoading) {
        return <div>Loading...</div>
    }

    return (
        <>
            {puzzleSolved && <div>Puzzle Solved!</div>}
            <div
                className="grid"
                onMouseUp={handleMouseUp}
                style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${grid.length}, 40px)`,
                    gridTemplateRows: `repeat(${grid.length}, 40px)`
                }}
            >
                {grid.map((row, rowIndex) =>
                    row.map((cell, colIndex) => (
                        <div
                            key={`${rowIndex}-${colIndex}`}
                            className="cell"
                            style={{
                                backgroundColor: cell.value ? intToColor(cell.value) : 'white',
                                filter: cell.isHead ? 'brightness(0.95)' : 'none',
                                width: '40px',
                                height: '40px'
                            }}
                            onMouseDown={() => handleMouseDown(rowIndex, colIndex)}
                            onMouseOver={() => handleMouseOver(rowIndex, colIndex)}
                        />
                    ))
                )}
            </div></>
    )
}

export default Grid
