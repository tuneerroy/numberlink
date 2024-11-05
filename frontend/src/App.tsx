import './App.css'
import Puzzle from './Puzzle'
import Solver from './Solver'

function App() {
  return (
    <div className="App">
      <h1>Numberlink Puzzle</h1>
      <Puzzle />

      <h2>Solver</h2>
      <Solver />
    </div>
  )
}

export default App
