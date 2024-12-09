def solver(f):
    def wrapper(puzzle):
        # Preprocess the puzzle
        all_numbers = {num for row in puzzle for num in row}
        all_numbers.add(0)

        mapping = {val: i for i, val in enumerate(sorted(all_numbers))}
        puzzle_cpy = [[mapping[val] for val in row] for row in puzzle]

        # Call the solver function
        result = f(puzzle_cpy)

        # Handle different return types
        if isinstance(result, tuple):  # Solver returns (solution, num_clauses)
            best_puzzle, num_clauses = result
        else:  # Solver returns only the solution
            best_puzzle = result
            num_clauses = None

        if best_puzzle is None:
            return None, None

        # Postprocess the solution
        new_mapping = dict()
        for i in range(len(puzzle)):
            for j in range(len(puzzle[i])):
                if puzzle[i][j] != 0:
                    new_mapping[best_puzzle[i][j]] = puzzle[i][j]
        for i in range(len(best_puzzle)):
            for j in range(len(best_puzzle[i])):
                best_puzzle[i][j] = new_mapping[best_puzzle[i][j]]

        return best_puzzle, num_clauses

    return wrapper
