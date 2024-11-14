import SolverGrid from './SolverGrid'
import { useEffect, useState } from 'react'

interface Range {
    min: number
    max: number
}

function Solver() {
    const [difficultyRange, setDifficultyRange] = useState<Range>({ min: 6, max: 12 })
    const [difficulty, setDifficulty] = useState(6)
    const [isLoading, setIsLoading] = useState(false)
    const [puzzle, setPuzzle] = useState<number[][]>([])
    const [error, setError] = useState('')
    const [editable, setEditable] = useState(true)

    const resetPuzzle = (length: number) => {
        setPuzzle(Array.from({ length }, () => Array.from({ length }, () => 0)))
        setEditable(true)
    }

    const solvePuzzle = async () => {
        setError('')
        setIsLoading(true)
        try {
            const res = await fetch('http://localhost:8000/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(puzzle),
            })
            const data = await res.json()
            if (!res.ok) {
                throw new Error(data.detail)
            }
            setPuzzle(data)
            setEditable(false)
        } catch (err: any) {
            if (err instanceof Error) {
                setError(err.message)
            }
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
                console.error("Difficulty range fetch error:", err)
            } finally {
                setIsLoading(false)
            }
        }

        getDifficultyRange()
    }, [])

    useEffect(() => {
        resetPuzzle(difficulty)
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
                    onClick={() => resetPuzzle(difficulty)}
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
                {error && <div className="error">Error: {error}</div>}
                {puzzle.length > 0 && <SolverGrid puzzle={puzzle} setPuzzle={setPuzzle} editable={editable} />}
            </div >
        </>
    )
}

export default Solver
