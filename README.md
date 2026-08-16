# Tic-Tac-Toe with AI

A Tic-Tac-Toe game with a graphical interface built using Pygame, featuring an unbeatable AI opponent powered by the Minimax algorithm.

## Author
**Saif Al Saad**<br>
🎓 BSc in **Software Engineering**<br>
🔍 Major in **Software Quality Assurance & Testing**<br>
🏫 **Daffodil International University**<br>

## Features

- Play as X or O against an AI opponent, or play locally with a friend in 2-Player mode
- Three AI difficulty levels: Low (random moves), Medium (shallow lookahead), and High (perfect play via Minimax — it never loses)
- Score tracker (X wins / O wins / Ties) that persists across rounds
- Smooth, animated interface: eased hover states, pop-in marks, animated win line, screen transitions
- Sound effects for moves, wins, and ties, with a mute toggle
- "Play Again" and "Back to Menu" options after each game

## Requirements

- Python 3
- Pygame

## Installation

1. Clone or download this repository.
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   ```
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the game with:
```bash
python runner.py
```

Choose a game mode (vs Computer or 2 Player). If playing the computer, choose your side (X or O) and a difficulty level (Low / Medium / High), then click on the board to make your move. The AI will respond automatically. Sound effects can be muted with the speaker icon in the top-right corner.

## Project Structure

```
.
├── runner.py             # Game loop and Pygame GUI
├── tictactoe.py           # Core game logic and Minimax AI
├── requirements.txt       # Python dependencies
├── OpenSans-Regular.ttf   # Font used in the GUI
└── README.md
```

## How the AI Works

The AI uses the **Minimax algorithm** to determine the optimal move at each turn:

- `player(board)` — determines whose turn it is
- `actions(board)` — lists all possible moves
- `result(board, action)` — returns the board after a move
- `winner(board)` — checks for a winner
- `terminal(board)` — checks if the game has ended
- `utility(board)` — scores a finished game (`1` for X win, `-1` for O win, `0` for a tie)
- `heuristic(board)` — evaluates a board from X's perspective without a full search (used at the search limit)
- `minimax(board)` — recursively explores all possible outcomes to choose the best move, assuming both players play optimally
- `minimax_limited(board, depth)` — a depth-limited version of Minimax that uses the heuristic when the search limit is reached
- `ai_move(board, difficulty)` — picks a move based on difficulty: `"Low"` plays randomly, `"Medium"` searches two plies ahead, and `"High"` plays optimally

Because both players play perfectly on **High** difficulty, a game between the AI (at High) and a human who also plays well will always end in a tie.

## License

This project is for educational purposes.