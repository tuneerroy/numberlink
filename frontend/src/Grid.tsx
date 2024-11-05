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

const Grid: React.FC<GridProps> = ({ puzzle, solution }) => {
    const [grid, setGrid] = useState<Cell[][]>(puzzle)
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

    const handleMouseUp = () => {
        setDragValue(null)
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
