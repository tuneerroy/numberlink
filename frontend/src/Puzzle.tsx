import Grid, { Cell } from './Grid'
import { useEffect, useState } from 'react'

interface Range {
    min: number
    max: number
}

function Puzzle() {
    const [difficultyRange, setDifficultyRange] = useState<Range>({ min: 6, max: 12 })
    const [difficulty, setDifficulty] = useState(6)

    const [puzzle, setPuzzle] = useState<Cell[][]>([])
    const [solution, setSolution] = useState<number[][]>([])

    const [isLoading, setIsLoading] = useState(false)

    const getPuzzle = async (difficulty: number) => {
        setIsLoading(true)
        try {
            const res = await fetch(`http://localhost:8000/puzzle?difficulty=${difficulty}`)
            const data = await res.json()
            setSolution(data.solution)
            setPuzzle(
                data.puzzle.map((row: number[]) =>
                    row.map(value => ({
                        value,
                        isHead: value !== 0
                    }))
                )
            )
        } catch (err) {
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

    if (isLoading) {
        return <div>Loading...</div>
    }

    return (
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
                onClick={() => getPuzzle(difficulty)}
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
                New Puzzle
            </button>
            <Grid puzzle={puzzle} solution={solution} />
        </div>
    )
}

export default Puzzle
