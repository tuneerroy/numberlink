import SolverGrid, { Cell } from './SolverGrid'
import { useEffect, useState } from 'react'

interface Range {
    min: number
    max: number
}

function Solver() {
    const [difficultyRange, setDifficultyRange] = useState<Range>({ min: 6, max: 12 })
    const [difficulty, setDifficulty] = useState(6)
    const [isLoading, setIsLoading] = useState(false)
    const [puzzle, setPuzzle] = useState<Cell[][]>([])
    const [hasError, setHasError] = useState(false)

    const resetPuzzle = () => {
        setPuzzle(Array.from({ length: difficulty }, () => Array.from({ length: difficulty }, () => ({ value: 0, isHead: false }))))
    }

    const solvePuzzle = async () => {
        setHasError(false)
        setIsLoading(true)
        try {
            const res = await fetch('http://localhost:8000/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ puzzle }),
            })
            const data = await res.json()
        } catch (err) {
            setHasError(true)
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        setIsLoading(true)

        const getDifficultyRange = async () => {
            try {
                const res = await fetch('http://localhost:8000/difficulty')
                const data = await res.json()
                setDifficultyRange(data)
                setDifficulty(data.min)
            } catch (err) {
                console.error(err)
            } finally {
                setIsLoading(false)
            }
        }

        getDifficultyRange()
    }, [])

    useEffect(() => {
        resetPuzzle()
    }, [difficulty])

    if (isLoading) {
        return <div>Loading...</div>
    }

    return (
        <>
            <div>
                <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(parseInt(e.target.value))}
                    style={{
                        padding: '8px 12px',
                        fontSize: '16px',
                        borderRadius: '5px',
                        border: '1px solid #ccc',
                        cursor: 'pointer',
                    }}
                >
                    {Array.from({ length: difficultyRange.max - difficultyRange.min + 1 }, (_, i) => i + difficultyRange.min).map(level => (
                        <option key={level} value={level}>
                            Difficulty {level}
                        </option>
                    ))}
                </select>

                <button
                    onClick={() => resetPuzzle()}
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
                    Reset
                </button>
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
                    Solve
                </button>
                {hasError && <div className="error">Something went wrong</div>}
                {puzzle.length > 0 && <SolverGrid puzzle={puzzle} setPuzzle={setPuzzle} />}
            </div >
        </>
    )
}

export default Solver
