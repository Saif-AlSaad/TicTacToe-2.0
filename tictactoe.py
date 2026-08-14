"""
Tic Tac Toe Player
"""

import math
import copy
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)

    # X always goes first, so if counts are equal it's X's turn,
    # otherwise it's O's turn.
    if x_count <= o_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action

    if i not in range(3) or j not in range(3):
        raise IndexError("Action out of bounds")
    if board[i][j] != EMPTY:
        raise ValueError("Invalid action: cell already taken")

    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    lines = []

    # Rows
    for i in range(3):
        lines.append([board[i][0], board[i][1], board[i][2]])

    # Columns
    for j in range(3):
        lines.append([board[0][j], board[1][j], board[2][j]])

    # Diagonals
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    for line in lines:
        if line[0] is not EMPTY and line[0] == line[1] == line[2]:
            return line[0]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    # If any cell is still empty, game is not over
    for row in board:
        if EMPTY in row:
            return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    current_player = player(board)

    if current_player == X:
        best_value = -math.inf
        best_action = None
        for action in actions(board):
            value = min_value(result(board, action))
            if value > best_value:
                best_value = value
                best_action = action
        return best_action
    else:
        best_value = math.inf
        best_action = None
        for action in actions(board):
            value = max_value(result(board, action))
            if value < best_value:
                best_value = value
                best_action = action
        return best_action


def heuristic(board):
    """
    Evaluates a board from X's perspective without full search.
    Positive values favor X, negative values favor O.
    """
    win = winner(board)
    if win == X:
        return 100
    elif win == O:
        return -100

    lines = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[0][2], board[1][1], board[2][0]],
    ]

    score = 0
    for line in lines:
        xs = line.count(X)
        os = line.count(O)
        if os == 0 and xs == 2:
            score += 10
        elif os == 0 and xs == 1:
            score += 1
        elif xs == 0 and os == 2:
            score -= 10
        elif xs == 0 and os == 1:
            score -= 1
    return score


def max_value_limited(board, depth):
    """
    Helper function: returns the maximum heuristic value achievable from
    this board state, searching at most `depth` plies ahead.
    """
    if terminal(board) or depth == 0:
        return heuristic(board)

    v = -math.inf
    for action in actions(board):
        v = max(v, min_value_limited(result(board, action), depth - 1))
    return v


def min_value_limited(board, depth):
    """
    Helper function: returns the minimum heuristic value achievable from
    this board state, searching at most `depth` plies ahead.
    """
    if terminal(board) or depth == 0:
        return heuristic(board)

    v = math.inf
    for action in actions(board):
        v = min(v, max_value_limited(result(board, action), depth - 1))
    return v


def minimax_limited(board, depth):
    """
    Returns the best action for the current player on the board, searching
    only `depth` plies ahead and using a heuristic at the search limit.
    """
    if terminal(board):
        return None

    current_player = player(board)

    if current_player == X:
        best_value = -math.inf
        best_action = None
        for action in actions(board):
            value = min_value_limited(result(board, action), depth - 1)
            if value > best_value:
                best_value = value
                best_action = action
        return best_action
    else:
        best_value = math.inf
        best_action = None
        for action in actions(board):
            value = max_value_limited(result(board, action), depth - 1)
            if value < best_value:
                best_value = value
                best_action = action
        return best_action


def ai_move(board, difficulty):
    """
    Returns the AI's action on the board based on the selected difficulty:
    "Low" picks randomly, "Medium" uses shallow lookahead, "High" plays optimally.
    """
    if difficulty == "Low":
        return random.choice(list(actions(board)))
    elif difficulty == "Medium":
        return minimax_limited(board, 2)
    else:
        return minimax(board)


def max_value(board):
    """
    Helper function: returns the maximum utility value achievable
    from this board state, assuming optimal play from both sides.
    """
    if terminal(board):
        return utility(board)

    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    """
    Helper function: returns the minimum utility value achievable
    from this board state, assuming optimal play from both sides.
    """
    if terminal(board):
        return utility(board)

    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v