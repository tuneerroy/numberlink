import React, { useEffect, useState } from 'react'

const intToColor = (num: number) => `hsl(${(num * 137.5) % 360}, 70%, 70%)`

export interface Cell {
    value: number
    isHead: boolean
}

interface GridProps {
    puzzle: Cell[][]
    setPuzzle: (puzzle: Cell[][]) => void
    solution: number[][]
}

const Grid: React.FC<GridProps> = ({ puzzle, setPuzzle, solution }) => {
    const [dragValue, setDragValue] = useState<number | null>(null)
    const [puzzleSolved, setPuzzleSolved] = useState(false)

    useEffect(() => {
        if (puzzle.length === 0 || puzzle.length !== solution.length) return
        const isSolved = puzzle.every((row, rowIndex) =>
            row.every((cell, colIndex) => {
                return cell.value === solution[rowIndex][colIndex]
            })
        )
        setPuzzleSolved(isSolved)
    }, [puzzle, solution])


    const handleMouseDown = (row: number, col: number) => {
        if (puzzleSolved) return
        const cell = puzzle[row][col]
        // only if non-zero value
        if (cell.value) {
            setDragValue(cell.value)
        }
    }

    const handleMouseOver = (row: number, col: number) => {
        if (puzzleSolved) return
        if (dragValue) {
            const newGrid = puzzle.map(row => row.map(cell => ({ ...cell })))
            if (!newGrid[row][col].isHead) {
                newGrid[row][col].value = dragValue
            }
            setPuzzle(newGrid)
        }
    }

    const handleMouseUp = () => {
        setDragValue(null)
    }

    return (
        <>
            <br />
            {puzzleSolved && <div>Puzzle Solved!</div>}
            <div
                className="grid"
                onMouseUp={handleMouseUp}
                style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${puzzle.length}, 40px)`,
                    gridTemplateRows: `repeat(${puzzle.length}, 40px)`
                }}
            >
                {puzzle.map((row, rowIndex) =>
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
