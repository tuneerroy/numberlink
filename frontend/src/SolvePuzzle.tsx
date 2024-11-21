import { useState } from 'react'

interface SolvePuzzleProps {
    puzzle: number[][]
    setPuzzle: (puzzle: number[][]) => void
    setError: (value: string) => void
    setEditable: (value: boolean) => void
}
type SolverIds = "CP-SAT Path Solver" | "PycoSAT Path Solver" | "PycoSAT Edge Solver"

function SolvePuzzle({ puzzle, setPuzzle, setError, setEditable }: SolvePuzzleProps) {
    const [solver, setSolver] = useState<SolverIds>("PycoSAT Edge Solver")
    const [loading, setLoading] = useState(false)

    const solvePuzzle = async () => {
        if (puzzle.length === 0) return

        let solverId
        switch (solver) {
            case "CP-SAT Path Solver":
                solverId = "ConstraintPathSolver"
                break
            case "PycoSAT Path Solver":
                solverId = "PycoPathSolver"
                break
            case "PycoSAT Edge Solver":
                solverId = "PycoEdgeSolver"
                break
            default:
                solverId = "PycoEdgeSolver"
                break
        }

        setError('')
        setLoading(true)
        try {
            const res = await fetch(`http://localhost:8000/solve/${solverId}`, {
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
            setLoading(false)
        }
    }


    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <select
                    value={solver}
                    onChange={e => setSolver(e.target.value as SolverIds)}
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
                    <option value="PycoSAT Edge Solver">PycoSAT Edge Solver</option>
                    <option value="PycoSAT Path Solver">PycoSAT Path Solver</option>
                    <option value="CP-SAT Path Solver">CP-SAT Path Solver</option>
                </select>
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
                    {loading ? "Solving..." : "Solve"}
                </button>
            </div >
        </>
    )
}

export default SolvePuzzle
