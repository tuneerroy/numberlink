import { useState } from 'react'


function Solver() {
    const [isLoading, setIsLoading] = useState(false)

    const solvePuzzle = async () => {
        setIsLoading(true)
        try {
            // const res = await fetch(`http://localhost:8000/puzzle?difficulty=${difficulty}`)
            // const data = await res.json()
            // setSolution(data.solution)
            // setPuzzle(
            //     data.puzzle.map((row: number[]) =>
            //         row.map(value => ({
            //             value,
            //             isHead: value !== 0
            //         }))
            //     )
            // )
        } catch (err) {
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }

    if (isLoading) {
        return <div>Loading...</div>
    }

    return (
        <div>
            <button
                onClick={() => solvePuzzle()}
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
                onMouseOver={e => e.currentTarget.style.backgroundColor = '#45a049'}
                onMouseOut={e => e.currentTarget.style.backgroundColor = '#4CAF50'}
            >
                Solve Puzzle
            </button>
        </div>
    )
}

export default Solver
