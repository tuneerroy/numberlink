import React, { useEffect, useState } from 'react'

interface GridProps {
}

const intToColor = (num: number) => `hsl(${(num * 137.5) % 360}, 70%, 70%)`

// Grid should be an array of Cells
// Each Cell should have a value and be either a head node

interface Cell {
    value: number
    isHead: boolean
}

const Grid: React.FC<GridProps> = () => {
    // const [grid, setGrid] = useState(Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i * n + j + 1) % (n * n + 1))))
    // grid should just be filled with 0s by default
    // set to empty array of cells 
    const [grid, setGrid] = useState<(Cell)[][]>([])
    const [dragValue, setDragValue] = useState<number | null>(null)

    useEffect(() => {
        // make a get request to the backend to get the grid
        fetch(`http://localhost:8000/puzzle/0`)
            .then(res => res.json())
            .then(data => {
                console.log(data)
                setGrid(
                    data.map((row: number[]) =>
                        row.map(value => ({
                            value,
                            isHead: value !== 0
                        }))
                    )
                )
            })
            .catch(err => console.error(err))
    }, [])

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

    return (
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
        </div>
    )
}

export default Grid
