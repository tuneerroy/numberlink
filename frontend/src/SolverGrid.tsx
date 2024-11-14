import React from 'react'

const intToColor = (num: number) => `hsl(${(num * 137.5) % 360}, 70%, 70%)`

interface SolverGridProps {
    puzzle: number[][]
    setPuzzle: React.Dispatch<React.SetStateAction<number[][]>>
    editable: boolean
}

const SolverGrid: React.FC<SolverGridProps> = ({ puzzle, setPuzzle, editable }) => {
    const handleMouseClicked = (row: number, col: number, incr: number) => {
        if (!editable) return

        const maxNum = Math.floor((puzzle.length * puzzle.length) / 2)
        puzzle[row][col] = (puzzle[row][col] + maxNum + 1 + incr) % (maxNum + 1)
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
                                backgroundColor: cell ? intToColor(cell) : 'white',
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
                            {cell ? cell : ''}
                        </div>
                    ))
                )}
            </div></>
    )
}

export default SolverGrid
