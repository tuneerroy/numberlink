import SolvePuzzle from './SolvePuzzle'
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
        setError('')
        setPuzzle(Array.from({ length }, () => Array.from({ length }, () => 0)))
        setEditable(true)
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
                if (err instanceof Error) {
                    setError(err.message)
                }
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
                        padding: '10px 20px',
                        margin: '10px 5px',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        borderRadius: '5px',
                        border: 'none',
                        backgroundColor: '#f1f1f1',
                        cursor: 'pointer'
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
                <SolvePuzzle puzzle={puzzle} setPuzzle={setPuzzle} setError={setError} setEditable={setEditable} />
                {error && <div className="error">Error: {error}</div>}
                {puzzle.length > 0 && <SolverGrid puzzle={puzzle} setPuzzle={setPuzzle} editable={editable} />}
            </div >
        </>
    )
}

export default Solver
