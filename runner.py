import pygame
import sys
import time

import tictactoe as ttt

pygame.init()
size = width, height = 600, 400

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
gray = (50, 50, 50)
lightGray = (200, 200, 200)
hoverGray = (95, 95, 95)
buttonFill = (70, 70, 70)
green = (46, 204, 113)
amber = (241, 196, 15)
red = (231, 76, 60)
panelFill = (35, 35, 40)
panelBorder = (60, 60, 70)
hoverFill = (58, 58, 68)
gridColor = (125, 125, 135)
xColor = (93, 173, 226)
oColor = (236, 112, 99)
winColor = (241, 196, 15)
winFill = (70, 65, 40)

screen = pygame.display.set_mode(size)

mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)
smallFont = pygame.font.Font("OpenSans-Regular.ttf", 16)

user = None
difficulty = None
board = ttt.initial_state()
ai_turn = False


def draw_mark(surface, center, mark, size, color):
    """
    Draws an X or O as a smooth vector shape centered on `center`.
    """
    cx, cy = center
    if mark == ttt.X:
        offset = int(size * 0.28)
        width = max(4, int(size * 0.12))
        pygame.draw.line(surface, color, (cx - offset, cy - offset), (cx + offset, cy + offset), width)
        pygame.draw.line(surface, color, (cx + offset, cy - offset), (cx - offset, cy + offset), width)
    else:
        pygame.draw.circle(surface, color, center, int(size * 0.32), max(4, int(size * 0.12)))


def winning_cells(board):
    """
    Returns the list of (i, j) cells that form the winning line, or None.
    """
    lines = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]
    for line in lines:
        marks = {board[i][j] for i, j in line}
        if len(marks) == 1 and ttt.EMPTY not in marks:
            return line
    return None

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(black)

    # Let user choose a player.
    if user is None:

        # Draw title
        title = largeFont.render("Play Tic-Tac-Toe", True, white)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 40)
        screen.blit(title, titleRect)

        subtitle = mediumFont.render("Choose your side", True, lightGray)
        subtitleRect = subtitle.get_rect()
        subtitleRect.center = ((width / 2), 90)
        screen.blit(subtitle, subtitleRect)

        mouse = pygame.mouse.get_pos()

        # Draw buttons
        options = [
            ("Play as X", "You go first", ttt.X, xColor),
            ("Play as O", "Computer goes first", ttt.O, oColor),
        ]
        buttons = []
        for index, (name, desc, mark, color) in enumerate(options):
            btn = pygame.Rect(0, 0, 180, 120)
            btn.center = ((width / 2) + (index - 0.5) * 200, height / 2 + 10)
            hovered = btn.collidepoint(mouse)

            fill = buttonFill if not hovered else hoverGray
            pygame.draw.rect(screen, fill, btn, border_radius=12)
            pygame.draw.rect(screen, color, btn, width=3, border_radius=12)

            draw_mark(screen, (btn.centerx, btn.top + 34), mark, 40, color)

            label = mediumFont.render(name, True, white)
            labelRect = label.get_rect()
            labelRect.midtop = (btn.centerx, btn.top + 66)
            screen.blit(label, labelRect)

            descText = smallFont.render(desc, True, lightGray)
            descRect = descText.get_rect()
            descRect.midtop = (btn.centerx, btn.top + 100)
            screen.blit(descText, descRect)

            buttons.append((btn, mark))

        # Check if button is clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            for btn, mark in buttons:
                if btn.collidepoint(mouse):
                    time.sleep(0.2)
                    user = mark

    elif difficulty is None:

        # Draw title
        title = largeFont.render("Choose AI Difficulty", True, white)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 40)
        screen.blit(title, titleRect)

        subtitle = mediumFont.render("How challenging should the computer be?", True, lightGray)
        subtitleRect = subtitle.get_rect()
        subtitleRect.center = ((width / 2), 90)
        screen.blit(subtitle, subtitleRect)

        mouse = pygame.mouse.get_pos()

        # Draw buttons
        options = [
            ("Low", "Random moves", green),
            ("Medium", "Balanced play", amber),
            ("High", "Perfect play", red),
        ]
        buttons = []
        for index, (name, desc, color) in enumerate(options):
            btn = pygame.Rect(0, 0, 170, 90)
            btn.center = ((width / 2) + (index - 1) * 190, height / 2)
            hovered = btn.collidepoint(mouse)

            fill = buttonFill if not hovered else hoverGray
            pygame.draw.rect(screen, fill, btn, border_radius=12)
            pygame.draw.rect(screen, color, btn, width=3, border_radius=12)

            label = mediumFont.render(name, True, white)
            labelRect = label.get_rect()
            labelRect.midtop = (btn.centerx, btn.top + 12)
            screen.blit(label, labelRect)

            descText = smallFont.render(desc, True, lightGray)
            descRect = descText.get_rect()
            descRect.midtop = (btn.centerx, btn.top + 52)
            screen.blit(descText, descRect)

            buttons.append((btn, name))

        # Check if button is clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            for btn, name in buttons:
                if btn.collidepoint(mouse):
                    time.sleep(0.2)
                    difficulty = name

    else:

        # Draw game board
        tile_size = 80
        board_size = 3 * tile_size
        board_origin = (width / 2 - board_size / 2,
                       height / 2 - board_size / 2 + 15)

        game_over = ttt.terminal(board)
        player = ttt.player(board)

        # Board panel
        panel = pygame.Rect(board_origin[0] - 20, board_origin[1] - 20,
                            board_size + 40, board_size + 40)
        pygame.draw.rect(screen, panelFill, panel, border_radius=16)
        pygame.draw.rect(screen, panelBorder, panel, width=2, border_radius=16)

        # Grid lines
        for i in range(1, 3):
            x = board_origin[0] + i * tile_size
            pygame.draw.line(screen, gridColor, (x, board_origin[1]),
                             (x, board_origin[1] + board_size), 4)
        for j in range(1, 3):
            y = board_origin[1] + j * tile_size
            pygame.draw.line(screen, gridColor, (board_origin[0], y),
                             (board_origin[0] + board_size, y), 4)

        mouse = pygame.mouse.get_pos()
        tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    board_origin[0] + j * tile_size,
                    board_origin[1] + i * tile_size,
                    tile_size, tile_size
                )

                # Hover highlight on empty cells during user's turn
                if (user == player and not game_over and
                        board[i][j] == ttt.EMPTY and rect.collidepoint(mouse)):
                    pygame.draw.rect(screen, hoverFill, rect.inflate(-6, -6), border_radius=8)

                if board[i][j] != ttt.EMPTY:
                    mark_color = xColor if board[i][j] == ttt.X else oColor
                    draw_mark(screen, rect.center, board[i][j], tile_size * 0.7, mark_color)

                row.append(rect)
            tiles.append(row)

        # Highlight the winning line
        win_line = winning_cells(board)
        if win_line:
            for i, j in win_line:
                pygame.draw.rect(screen, winFill, tiles[i][j].inflate(-6, -6), border_radius=8)
                mark_color = xColor if board[i][j] == ttt.X else oColor
                draw_mark(screen, tiles[i][j].center, board[i][j], tile_size * 0.7, mark_color)

            start = tiles[win_line[0][0]][win_line[0][1]].center
            end = tiles[win_line[2][0]][win_line[2][1]].center
            pygame.draw.line(screen, winColor, start, end, 6)

        # Show title
        if game_over:
            winner = ttt.winner(board)
            if winner is None:
                title = f"Game Over: Tie."
            else:
                title = f"Game Over: {winner} wins."
        elif user == player:
            title = f"Play as {user}"
        else:
            title = f"Computer thinking..."
        title = largeFont.render(title, True, white)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 30)
        screen.blit(title, titleRect)

        diffText = smallFont.render(f"Difficulty: {difficulty}", True, lightGray)
        diffRect = diffText.get_rect()
        diffRect.center = ((width / 2), 60)
        screen.blit(diffText, diffRect)

        # Check for AI move
        if user != player and not game_over:
            if ai_turn:
                time.sleep(0.5)
                move = ttt.ai_move(board, difficulty)
                board = ttt.result(board, move)
                ai_turn = False
            else:
                ai_turn = True

        # Check for a user move
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1 and user == player and not game_over:
            mouse = pygame.mouse.get_pos()
            for i in range(3):
                for j in range(3):
                    if (board[i][j] == ttt.EMPTY and tiles[i][j].collidepoint(mouse)):
                        board = ttt.result(board, (i, j))

        if game_over:
            againButton = pygame.Rect(width / 3, height - 65, width / 3, 50)
            again = mediumFont.render("Play Again", True, white)
            againRect = again.get_rect()
            againRect.center = againButton.center
            pygame.draw.rect(screen, buttonFill, againButton, border_radius=12)
            pygame.draw.rect(screen, panelBorder, againButton, width=2, border_radius=12)
            screen.blit(again, againRect)
            click, _, _ = pygame.mouse.get_pressed()
            if click == 1:
                mouse = pygame.mouse.get_pos()
                if againButton.collidepoint(mouse):
                    time.sleep(0.2)
                    user = None
                    difficulty = None
                    board = ttt.initial_state()
                    ai_turn = False

    pygame.display.flip()
