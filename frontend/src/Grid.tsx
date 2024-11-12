import React, { useEffect, useState } from 'react'

const intToColor = (num: number) => `hsl(${(num * 137.5) % 360}, 70%, 70%)`

export interface Cell {
    value: number
    isHead: boolean
}

interface GridProps {
    puzzle: Cell[][]
    solution: number[][]
}

const copyPuzzle = (puzzle: Cell[][]) => puzzle.map(row => row.map(cell => ({ ...cell })))

const Grid: React.FC<GridProps> = ({ puzzle, solution }) => {
    const [grid, setGrid] = useState<Cell[][]>(copyPuzzle(puzzle))
    const [dragValue, setDragValue] = useState<number | null>(null)
    const [puzzleSolved, setPuzzleSolved] = useState(false)

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
        if (puzzleSolved) return
        const cell = grid[row][col]
        // only if non-zero value
        if (cell) {
            setDragValue(cell.value)
        }
    }

    const handleMouseOver = (row: number, col: number) => {
        if (puzzleSolved) return
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

    const setSolution = () => {
        const newGrid = grid.map(row => row.map(cell => ({ ...cell })))
        for (let i = 0; i < solution.length; i++) {
            for (let j = 0; j < solution.length; j++) {
                newGrid[i][j].value = solution[i][j]
            }
        }
        setGrid(newGrid)
    }

    const handleMouseUp = () => {
        setDragValue(null)
    }

    return (
        <>
            <br />
            <button
                onClick={() => setGrid(copyPuzzle(puzzle))}
                style={{
                    padding: '10px 20px',
                    margin: '10px 5px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    borderRadius: '5px',
                    border: 'none',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    cursor: 'pointer',
                    transition: 'background-color 0.3s ease'
                }}
            >Reset</button>
            <button
                onClick={() => setSolution()}
                style={{
                    padding: '10px 20px',
                    margin: '10px 5px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    borderRadius: '5px',
                    border: 'none',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    cursor: 'pointer',
                    transition: 'background-color 0.3s ease'
                }}
            >Solve</button>
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
                                height: '40px',
                                textAlign: 'center',
                                lineHeight: '40px',
                                userSelect: 'none'
                            }}
                            onMouseDown={() => handleMouseDown(rowIndex, colIndex)}
                            onMouseOver={() => handleMouseOver(rowIndex, colIndex)}
                        >
                            {cell.value ? cell.value : ''}
                        </div>
                    ))
                )}
            </div></>
    )
}

export default Grid
