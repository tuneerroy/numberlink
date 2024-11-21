def solver(f):
    def wrapper(puzzle):
        all_numbers = {num for row in puzzle for num in row}
        all_numbers.add(0)

        mapping = {val: i for i, val in enumerate(sorted(all_numbers))}
        puzzle_cpy = [[mapping[val] for val in row] for row in puzzle]

        best_puzzle = f(puzzle_cpy)
        if best_puzzle is None:
            return None

        new_mapping = dict()
        for i in range(len(puzzle)):
            for j in range(len(puzzle[i])):
                if puzzle[i][j] != 0:
                    new_mapping[best_puzzle[i][j]] = puzzle[i][j]
        for i in range(len(best_puzzle)):
            for j in range(len(best_puzzle[i])):
                best_puzzle[i][j] = new_mapping[best_puzzle[i][j]]
        return best_puzzle

    return wrapper
