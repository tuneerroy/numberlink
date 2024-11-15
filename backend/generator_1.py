import random

# Current path number
pathNum = 0
# Number of squares covered by paths
covered = 0


# Returns a board of the specified size. Each cell of the board is empty.
def GetEmptyBoard(size):
    return [[0 for _ in range(size)] for _ in range(size)]


# Returns the number of neighbours of cell (k, l) that have already been added
# to a path.
def NumAddedNeighbours(board, k, l):
    n = len(board)
    cnt = 0
    if k == 0:
        cnt += 1
    elif board[k - 1][l]:
        cnt += 1
    if k == n - 1:
        cnt += 1
    elif board[k + 1][l]:
        cnt += 1
    if l == 0:
        cnt += 1
    elif board[k][l - 1]:
        cnt += 1
    if l == n - 1:
        cnt += 1
    elif board[k][l + 1]:
        cnt += 1
    return cnt


# Returns the number of neighbours of cell (k, l) that are of the same pair
def NumSamePairNeighbours(board, k, l, pair):
    n = len(board)
    cnt = 0
    if k != 0 and board[k - 1][l] == pair:
        cnt += 1
    if k != n - 1 and board[k + 1][l] == pair:
        cnt += 1
    if l != 0 and board[k][l - 1] == pair:
        cnt += 1
    if l != n - 1 and board[k][l + 1] == pair:
        cnt += 1
    return cnt


# Returns whether adding cell (k, l) to the path causes one or more isolated
# uncovered squares.
def HasIsolatedSquares(board, k, l, pair, isLastNode):
    n = len(board)
    if isLastNode:
        if (
            k != 0
            and board[k - 1][l] == 0
            and NumAddedNeighbours(board, k - 1, l) == 4
            and NumSamePairNeighbours(board, k - 1, l, pair) > 1
        ):
            return True
        if (
            k != n - 1
            and board[k + 1][l] == 0
            and NumAddedNeighbours(board, k + 1, l) == 4
            and NumSamePairNeighbours(board, k + 1, l, pair) > 1
        ):
            return True
        if (
            l != 0
            and board[k][l - 1] == 0
            and NumAddedNeighbours(board, k, l - 1) == 4
            and NumSamePairNeighbours(board, k, l - 1, pair) > 1
        ):
            return True
        if (
            l != n - 1
            and board[k][l + 1] == 0
            and NumAddedNeighbours(board, k, l + 1) == 4
            and NumSamePairNeighbours(board, k, l + 1, pair) > 1
        ):
            return True
    else:
        if k != 0 and board[k - 1][l] == 0 and NumAddedNeighbours(board, k - 1, l) == 4:
            return True
        if (
            k != n - 1
            and board[k + 1][l] == 0
            and NumAddedNeighbours(board, k + 1, l) == 4
        ):
            return True
        if l != 0 and board[k][l - 1] == 0 and NumAddedNeighbours(board, k, l - 1) == 4:
            return True
        if (
            l != n - 1
            and board[k][l + 1] == 0
            and NumAddedNeighbours(board, k, l + 1) == 4
        ):
            return True
    return False


# Locates and returns a random uncovered neighbour of cell (i, j). Additional
# constraints are enforced during path extension if a non-zero 'pair' is
# passed. This function ensures that the neighbour returned does not lead to
# any isolated uncovered squares.
def GetPathExtensionNeighbour(board, i, j, pair):
    n = len(board)
    u = random.randint(0, 3)
    for v in range(4):
        u = (u + 1) % 4
        i1, j1 = i, j
        if u == 0:
            if i == 0:
                continue
            i1 = i - 1
        elif u == 1:
            if j == n - 1:
                continue
            j1 = j + 1
        elif u == 2:
            if j == 0:
                continue
            j1 = j - 1
        elif u == 3:
            if i == n - 1:
                continue
            i1 = i + 1
        # Found an uncovered neighbour.
        if board[i1][j1] == 0:
            # Check the pair constraint.
            if pair:
                if NumSamePairNeighbours(board, i1, j1, pair) > 1:
                    continue
            board[i1][j1] = pair
            # Check whether this neighbour causes isolated empty cells.
            if HasIsolatedSquares(board, i, j, pair, False) or HasIsolatedSquares(
                board, i1, j1, pair, True
            ):
                board[i1][j1] = 0
                continue
            # This neighbour is suitable for path extension.
            return [i1, j1]
    # None of the 4 neighbours can extend the path, so return fail.
    return [0, 0]


# Tries to add a random path to the board, and returns whether it was
# successful.
def AddPath(board_unsolved, board_solved):
    global pathNum, covered
    n = len(board_unsolved)
    # Use the next pair.
    pathNum += 1
    # Try and locate uncovered neighboring squares (i,j) and (k,l).
    s = random.randint(0, n * n - 1)
    for t in range(n * n):
        s = (s + 1) % (n * n)
        i = s // n
        j = s % n
        if board_solved[i][j] == 0:
            board_unsolved[i][j] = pathNum
            board_solved[i][j] = pathNum
            if HasIsolatedSquares(board_solved, i, j, pathNum, True):
                board_solved[i][j] = 0
                board_unsolved[i][j] = 0
                continue
            else:
                nbr = GetPathExtensionNeighbour(board_solved, i, j, pathNum)
                if nbr[0] == 0 and nbr[1] == 0:
                    board_solved[i][j] = 0
                    board_unsolved[i][j] = 0
                    continue
                else:
                    # Found path starting with (i, j) and nbr.
                    break
    else:
        # Backtrack
        pathNum -= 1
        return False

    pathlen = 2
    covered += 2
    while True:
        i = nbr[0]
        j = nbr[1]
        nextNbr = GetPathExtensionNeighbour(board_solved, i, j, pathNum)
        if (nextNbr[0] != 0 or nextNbr[1] != 0) and pathlen < n * n:
            nbr = nextNbr
        else:
            board_unsolved[nbr[0]][nbr[1]] = pathNum
            return True
        pathlen += 1
        covered += 1


# Returns a random permutation of array using Fisher-Yates method.
def Shuffle(array):
    currentIndex = len(array)
    while currentIndex != 0:
        randomIndex = random.randint(0, currentIndex - 1)
        currentIndex -= 1
        array[currentIndex], array[randomIndex] = (
            array[randomIndex],
            array[currentIndex],
        )
    return array


# Shuffles the pairs on the board since by this method, paths generated
# earlier will be longer.
def ShufflePairs(board_unsolved, board_solved, numPairs):
    nums = [i for i in range(1, numPairs + 1)]
    nums = Shuffle(nums)
    n = len(board_unsolved)
    for i in range(n):
        for j in range(n):
            if board_unsolved[i][j] != 0:
                board_unsolved[i][j] = nums[board_unsolved[i][j] - 1]
            board_solved[i][j] = nums[board_solved[i][j] - 1]


def GenerateBoard(size):
    global pathNum, covered
    board_unsolved = GetEmptyBoard(size)
    board_solved = GetEmptyBoard(size)
    # Randomized Numberlink board generation strategy. Repeat until all
    # squares are covered and satisfy the constraints.
    while True:
        board_unsolved = GetEmptyBoard(size)
        board_solved = GetEmptyBoard(size)
        pathNum = 0
        covered = 0
        while AddPath(board_unsolved, board_solved):
            continue
        if covered >= size * size:
            break
    ShufflePairs(board_unsolved, board_solved, pathNum)
    return board_unsolved
