import { useState } from 'react'


export interface Range {
    min: number
    max: number
}

interface SolvePuzzleProps {
    setPuzzle: (puzzle: number[][]) => void
    setSolution: (solution: number[][]) => void
    setError: (value: string) => void
    setLoading: (value: boolean) => void
    difficultyRange: Range
}

type GeneratorIds = 0 | 1 | 2

function GetPuzzle({ setPuzzle, setError, setLoading, difficultyRange }: SolvePuzzleProps) {
    const [difficulty, setDifficulty] = useState(difficultyRange.min)
    const [generator, setGenerator] = useState<GeneratorIds>(0)

    const generatePuzzle = async () => {
        setError('')
        setLoading(true)
        try {
            const res = await fetch(`http://localhost:8000/puzzle/${generator}?difficulty=${difficulty}`)
            const data = await res.json()
            setPuzzle(data.puzzle)
        } catch (err: any) {
            if (err instanceof Error) {
                setError(err.message)
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
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
                <select
                    value={generator}
                    onChange={e => setGenerator(parseInt(e.target.value) as GeneratorIds)}
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
                    <option value={0}>Generator #1</option>
                    <option value={1}>Generator #2</option>
                    <option value={2}>Generator #3</option>
                </select>
                <button
                    onClick={() => generatePuzzle()}
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
                    Generate Puzzle
                </button>
            </div >
        </>
    )
}

export default GetPuzzle
