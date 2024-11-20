import Grid, { Cell } from './Grid'
import { useEffect, useState } from 'react'
import SolvePuzzle from './SolvePuzzle'
import GetPuzzle, { Range } from './GetPuzzle'

function Puzzle() {
    const [puzzle, setPuzzle] = useState<Cell[][]>([])
    const [puzzleCopy, setPuzzleCopy] = useState<Cell[][]>([])
    const [solution, setSolution] = useState<number[][]>([])
    const [difficultyRange, setDifficultyRange] = useState<Range>({ min: 6, max: 12 })

    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        setIsLoading(true)

        const getDifficultyRange = async () => {
            try {
                const res = await fetch('http://localhost:8000/difficulty')
                const data = await res.json()
                setDifficultyRange(data)
            } catch (err) {
                console.error("Difficulty range fetch error:", err)
            } finally {
                setIsLoading(false)
            }
        }

        getDifficultyRange()
    }, [])

    const gridToPuzzle = (puzzle: number[][]) => {
        setPuzzle(
            puzzle.map((row: number[]) =>
                row.map(value => ({
                    value,
                    isHead: value !== 0
                }))
            )
        )
        setPuzzleCopy(
            puzzle.map((row: number[]) =>
                row.map(value => ({
                    value,
                    isHead: value !== 0
                }))
            )
        )
    }

    const copyPuzzle = (puzzle: Cell[][]) => puzzle.map(row => row.map(cell => ({ ...cell })))

    const resetPuzzle = () => {
        setPuzzle(copyPuzzle(puzzleCopy))
    }

    if (isLoading) {
        return <div>Loading...</div>
    }

    return (
        <div>
            <GetPuzzle
                setPuzzle={gridToPuzzle}
                setSolution={setSolution}
                setError={setError}
                setLoading={setIsLoading}
                difficultyRange={difficultyRange}
            />
            {error && <div className="error">Error: {error}</div>}
            {puzzle.length > 0 &&
                <>
                    <SolvePuzzle
                        puzzle={puzzleCopy.map(row => row.map(cell => cell.value))}
                        setPuzzle={(puzzle: number[][]) => setPuzzle(puzzle.map(row => row.map(value => ({ value, isHead: false }))))}
                        setError={setError}
                        setEditable={() => { }}
                    />
                    <button
                        onClick={resetPuzzle}
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
                    >Reset</button>
                    <Grid puzzle={puzzle} setPuzzle={setPuzzle} solution={solution} />
                </>
            }
        </div>
    )
}

export default Puzzle
