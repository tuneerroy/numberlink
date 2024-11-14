import React from 'react'

const intToColor = (num: number) => `hsl(${(num * 137.5) % 360}, 70%, 70%)`

export interface Cell {
    value: number
    isHead: boolean
}

interface SolverGridProps {
    puzzle: Cell[][]
    setPuzzle: React.Dispatch<React.SetStateAction<Cell[][]>>
}

const SolverGrid: React.FC<SolverGridProps> = ({ puzzle, setPuzzle }) => {
    const handleMouseClicked = (row: number, col: number, incr: number) => {
        const cell = puzzle[row][col]
        const maxNum = Math.floor((puzzle.length * puzzle.length) / 2)
        cell.value = (cell.value + maxNum + 1 + incr) % (maxNum + 1)
        setPuzzle([...puzzle])
    }

    const onLeftClick = (row: number, col: number) => {
        handleMouseClicked(row, col, 1)
    }

    const onRightClick = (row: number, col: number) => {
        handleMouseClicked(row, col, -1)
    }

    return (
        <>
            <div
                className="grid"
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
                            className="cell solver"
                            style={{
                                backgroundColor: cell.value ? intToColor(cell.value) : 'white',
                                filter: cell.isHead ? 'brightness(0.95)' : 'none',
                                width: '40px',
                                height: '40px',
                                textAlign: 'center',
                                lineHeight: '40px',
                                userSelect: 'none'
                            }}
                            onClick={() => onLeftClick(rowIndex, colIndex)}
                            onContextMenu={(e) => {
                                e.preventDefault()
                                onRightClick(rowIndex, colIndex)
                            }}
                        >
                            {cell.value ? cell.value : ''}
                        </div>
                    ))
                )}
            </div></>
    )
}

export default SolverGrid
