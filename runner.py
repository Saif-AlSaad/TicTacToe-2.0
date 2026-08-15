import math
import sys
import time

import pygame

import tictactoe as ttt

pygame.init()
size = width, height = 640, 520

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
bgTop = (18, 18, 24)
bgBottom = (10, 10, 14)
white = (245, 245, 248)
lightGray = (170, 170, 182)
faintGray = (110, 110, 122)
buttonFill = (42, 42, 52)
hoverFill = (54, 54, 68)
panelFill = (28, 28, 36)
panelBorder = (52, 52, 66)
gridColor = (70, 70, 86)
green = (52, 199, 123)
amber = (245, 200, 66)
red = (235, 87, 87)
cellHover = (44, 44, 58)
xColor = (99, 179, 237)
oColor = (240, 130, 118)
winColor = (245, 200, 66)
winFill = (58, 52, 32)
accent = (124, 131, 253)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Tic-Tac-Toe")
clock = pygame.time.Clock()

mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 26)
largeFont = pygame.font.Font("OpenSans-Regular.ttf", 38)
smallFont = pygame.font.Font("OpenSans-Regular.ttf", 15)
tinyFont = pygame.font.Font("OpenSans-Regular.ttf", 13)
scoreFont = pygame.font.Font("OpenSans-Regular.ttf", 20)

# ---------------------------------------------------------------------------
# Sound — synthesized in-memory, so the game needs no external audio files.
# Falls back to silent operation if the machine has no audio device at all.
# ---------------------------------------------------------------------------
sound_enabled = True
snd_place_x = snd_place_o = snd_win = snd_tie = snd_click = None
try:
    import numpy as np

    pygame.mixer.init(frequency=44100, size=-16, channels=2)

    def make_tone(freq, duration=0.11, volume=0.22, fade=True):
        sample_rate = 44100
        n = int(sample_rate * duration)
        t = np.linspace(0, duration, n, False)
        wave = np.sin(freq * t * 2 * np.pi)
        if fade:
            wave *= np.linspace(1, 0, n)
        audio = (wave * volume * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio)).copy(order="C")
        return pygame.sndarray.make_sound(stereo)

    def make_chime(freqs, duration=0.14, volume=0.22):
        """Plays a short sequence of tones back-to-back as one sound."""
        sample_rate = 44100
        n = int(sample_rate * duration)
        parts = []
        for f in freqs:
            t = np.linspace(0, duration, n, False)
            wave = np.sin(f * t * 2 * np.pi) * np.linspace(1, 0, n)
            parts.append(wave)
        full = np.concatenate(parts)
        audio = (full * volume * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio)).copy(order="C")
        return pygame.sndarray.make_sound(stereo)

    snd_place_x = make_tone(520)
    snd_place_o = make_tone(400)
    snd_win = make_chime([523, 659, 784])
    snd_tie = make_chime([392, 349])
    snd_click = make_tone(300, duration=0.05, volume=0.15)
except Exception:
    sound_enabled = False


def play_sound(snd):
    if sound_enabled and not muted and snd is not None:
        try:
            snd.play()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Easing helpers
# ---------------------------------------------------------------------------
def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1 - pow(1 - t, 3)


def ease_out_back(t, overshoot=1.7):
    t = max(0.0, min(1.0, t))
    return 1 + (overshoot + 1) * pow(t - 1, 3) + overshoot * pow(t - 1, 2)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def make_gradient(w, h, top, bottom):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        pygame.draw.line(surf, lerp_color(top, bottom, t), (0, y), (w, y))
    return surf


background = make_gradient(width, height, bgTop, bgBottom)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
hover_scales = {}
move_times = {}
screen_fade = 0.0
last_screen_key = None
win_started_at = None
last_win_line = None
dot_phase = 0.0
outcome_sound_played = False

game_mode = None    # "AI" or "2P"
user = None          # human's mark in AI mode; unused in 2P mode
difficulty = None
board = ttt.initial_state()
ai_turn = False
ai_move_ready_at = None
muted = False
score = {ttt.X: 0, ttt.O: 0, "Tie": 0}


def get_hover_scale(key, hovered, dt, speed=14.0):
    """Frame-rate-independent exponential smoothing toward a hover target."""
    current = hover_scales.get(key, 1.0)
    target = 1.05 if hovered else 1.0
    t = 1 - math.exp(-speed * dt)
    current = lerp(current, target, t)
    hover_scales[key] = current
    return current


def draw_button(surface, rect, hovered, dt, key, fill=buttonFill, border=None):
    scale = get_hover_scale(key, hovered, dt)
    grown = rect.inflate(rect.width * (scale - 1), rect.height * (scale - 1))
    fill_color = lerp_color(fill, hoverFill, ease_out_cubic((scale - 1) / 0.05))
    pygame.draw.rect(surface, fill_color, grown, border_radius=14)
    if border:
        pygame.draw.rect(surface, border, grown, width=2, border_radius=14)
    return grown


def draw_mark(surface, center, mark, mark_size, color, progress=1.0):
    scale = max(0.0, ease_out_back(progress))
    s = mark_size * scale
    cx, cy = center
    if mark == ttt.X:
        offset = int(s * 0.28)
        w = max(3, int(s * 0.12))
        pygame.draw.line(surface, color, (cx - offset, cy - offset), (cx + offset, cy + offset), w)
        pygame.draw.line(surface, color, (cx + offset, cy - offset), (cx - offset, cy + offset), w)
    else:
        radius = int(s * 0.32)
        w = max(3, int(s * 0.12))
        if radius > 0:
            pygame.draw.circle(surface, color, center, radius, w)


def winning_cells(board):
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


def set_screen(key):
    global last_screen_key, screen_fade
    if key != last_screen_key:
        last_screen_key = key
        screen_fade = 1.0


def new_round():
    """Resets the board for another round, keeping mode/side/difficulty/score."""
    global board, ai_turn, ai_move_ready_at, move_times
    global win_started_at, last_win_line, outcome_sound_played
    board = ttt.initial_state()
    ai_turn = False
    ai_move_ready_at = None
    move_times = {}
    win_started_at = None
    last_win_line = None
    outcome_sound_played = False


def back_to_menu():
    """Full reset: mode, side, difficulty, score, board."""
    global game_mode, user, difficulty, score
    game_mode = None
    user = None
    difficulty = None
    score = {ttt.X: 0, ttt.O: 0, "Tie": 0}
    new_round()


def draw_speaker_icon(surface, rect, is_muted):
    cx, cy = rect.center
    color = faintGray if is_muted else lightGray
    body = [(cx - 9, cy - 4), (cx - 4, cy - 4), (cx + 3, cy - 10), (cx + 3, cy + 10), (cx - 4, cy + 4), (cx - 9, cy + 4)]
    pygame.draw.polygon(surface, color, body)
    if is_muted:
        pygame.draw.line(surface, red, (cx + 6, cy - 8), (cx + 15, cy + 8), 2)
        pygame.draw.line(surface, red, (cx + 15, cy - 8), (cx + 6, cy + 8), 2)
    else:
        pygame.draw.arc(surface, color, (cx + 5, cy - 8, 14, 16), -0.9, 0.9, 2)
        pygame.draw.arc(surface, color, (cx + 8, cy - 11, 18, 22), -0.9, 0.9, 2)


def draw_mute_toggle(dt):
    """Top-right mute button, drawn on every screen. Returns its rect."""
    rect = pygame.Rect(0, 0, 40, 40)
    rect.topright = (width - 14, 14)
    hovered = rect.collidepoint(mouse)
    grown = draw_button(screen, rect, hovered, dt, key="mute", border=panelBorder)
    draw_speaker_icon(screen, grown, muted)
    return rect


def draw_score_bar(center_x, y):
    entries = [
        (f"X  {score[ttt.X]}", xColor),
        (f"Ties  {score['Tie']}", faintGray),
        (f"O  {score[ttt.O]}", oColor),
    ]
    gap = 130
    start_x = center_x - gap
    for idx, (text, color) in enumerate(entries):
        label = scoreFont.render(text, True, color)
        screen.blit(label, label.get_rect(center=(start_x + idx * gap, y)))


while True:
    dt = clock.tick(60) / 1000.0
    now = time.time()
    mouse = pygame.mouse.get_pos()

    clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = True

    screen.blit(background, (0, 0))

    mute_rect = draw_mute_toggle(dt)
    if clicked and mute_rect.collidepoint(mouse):
        muted = not muted
        if not muted:
            play_sound(snd_click)

    # -----------------------------------------------------------------
    # Screen 0: choose game mode
    # -----------------------------------------------------------------
    if game_mode is None:
        set_screen("mode_select")

        title = largeFont.render("Tic-Tac-Toe", True, white)
        screen.blit(title, title.get_rect(center=(width / 2, 65)))

        subtitle = mediumFont.render("Choose a game mode", True, lightGray)
        screen.blit(subtitle, subtitle.get_rect(center=(width / 2, 110)))

        options = [
            ("vs Computer", "Play against the AI", accent),
            ("2 Player", "Play locally with a friend", green),
        ]
        buttons = []
        for index, (name, desc, color) in enumerate(options):
            btn = pygame.Rect(0, 0, 220, 120)
            btn.center = ((width / 2) + (index - 0.5) * 250, height / 2)
            hovered = btn.collidepoint(mouse)
            grown = draw_button(screen, btn, hovered, dt, key=f"mode_{index}", border=color)

            label = mediumFont.render(name, True, white)
            screen.blit(label, label.get_rect(midtop=(grown.centerx, grown.top + 26)))

            descText = smallFont.render(desc, True, lightGray)
            screen.blit(descText, descText.get_rect(midtop=(grown.centerx, grown.top + 62)))

            buttons.append((btn, name))

        if clicked:
            for btn, name in buttons:
                if btn.collidepoint(mouse):
                    game_mode = "AI" if name == "vs Computer" else "2P"
                    play_sound(snd_click)

    # -----------------------------------------------------------------
    # Screen 1 (AI mode only): choose side
    # -----------------------------------------------------------------
    elif game_mode == "AI" and user is None:
        set_screen("choose_side")

        title = largeFont.render("Play Tic-Tac-Toe", True, white)
        screen.blit(title, title.get_rect(center=(width / 2, 55)))

        subtitle = mediumFont.render("Choose your side", True, lightGray)
        screen.blit(subtitle, subtitle.get_rect(center=(width / 2, 100)))

        options = [
            ("Play as X", "You go first", ttt.X, xColor),
            ("Play as O", "Computer goes first", ttt.O, oColor),
        ]
        buttons = []
        for index, (name, desc, mark, color) in enumerate(options):
            btn = pygame.Rect(0, 0, 190, 130)
            btn.center = ((width / 2) + (index - 0.5) * 230, height / 2 + 20)
            hovered = btn.collidepoint(mouse)
            grown = draw_button(screen, btn, hovered, dt, key=f"side_{index}", border=color)

            draw_mark(screen, (grown.centerx, grown.top + 38), mark, 44, color)

            label = mediumFont.render(name, True, white)
            screen.blit(label, label.get_rect(midtop=(grown.centerx, grown.top + 72)))

            descText = smallFont.render(desc, True, lightGray)
            screen.blit(descText, descText.get_rect(midtop=(grown.centerx, grown.top + 106)))

            buttons.append((btn, mark))

        if clicked:
            for btn, mark in buttons:
                if btn.collidepoint(mouse):
                    user = mark
                    play_sound(snd_click)

    # -----------------------------------------------------------------
    # Screen 2 (AI mode only): choose difficulty
    # -----------------------------------------------------------------
    elif game_mode == "AI" and difficulty is None:
        set_screen("choose_difficulty")

        title = largeFont.render("Choose AI Difficulty", True, white)
        screen.blit(title, title.get_rect(center=(width / 2, 55)))

        subtitle = mediumFont.render("How challenging should the computer be?", True, lightGray)
        screen.blit(subtitle, subtitle.get_rect(center=(width / 2, 100)))

        options = [
            ("Low", "Random moves", green),
            ("Medium", "Balanced play", amber),
            ("High", "Perfect play", red),
        ]
        buttons = []
        for index, (name, desc, color) in enumerate(options):
            btn = pygame.Rect(0, 0, 165, 100)
            btn.center = ((width / 2) + (index - 1) * 210, height / 2 + 10)
            hovered = btn.collidepoint(mouse)
            grown = draw_button(screen, btn, hovered, dt, key=f"diff_{index}", border=color)

            label = mediumFont.render(name, True, white)
            screen.blit(label, label.get_rect(midtop=(grown.centerx, grown.top + 16)))

            descText = smallFont.render(desc, True, lightGray)
            screen.blit(descText, descText.get_rect(midtop=(grown.centerx, grown.top + 58)))

            buttons.append((btn, name))

        if clicked:
            for btn, name in buttons:
                if btn.collidepoint(mouse):
                    difficulty = name
                    play_sound(snd_click)

    # -----------------------------------------------------------------
    # Screen 3: the game itself (both modes)
    # -----------------------------------------------------------------
    else:
        set_screen("game")

        # "Back to Menu" button, top-left
        menuButton = pygame.Rect(0, 0, 110, 34)
        menuButton.topleft = (14, 14)
        menuHovered = menuButton.collidepoint(mouse)
        menuGrown = draw_button(screen, menuButton, menuHovered, dt, key="menu", border=panelBorder)
        menuLabel = tinyFont.render("< Menu", True, lightGray)
        screen.blit(menuLabel, menuLabel.get_rect(center=menuGrown.center))
        if clicked and menuButton.collidepoint(mouse):
            back_to_menu()
            play_sound(snd_click)
            continue

        tile_size = 90
        board_size = 3 * tile_size
        board_origin = (width / 2 - board_size / 2, height / 2 - board_size / 2 + 32)

        game_over = ttt.terminal(board)
        player = ttt.player(board)

        # In 2P mode both sides are human; in AI mode only `user` clicks.
        human_can_click = (game_mode == "2P") or (game_mode == "AI" and user == player)

        panel = pygame.Rect(board_origin[0] - 22, board_origin[1] - 22,
                             board_size + 44, board_size + 44)
        pygame.draw.rect(screen, panelFill, panel, border_radius=18)
        pygame.draw.rect(screen, panelBorder, panel, width=2, border_radius=18)

        for i in range(1, 3):
            x = board_origin[0] + i * tile_size
            pygame.draw.line(screen, gridColor, (x, board_origin[1]),
                              (x, board_origin[1] + board_size), 3)
        for j in range(1, 3):
            y = board_origin[1] + j * tile_size
            pygame.draw.line(screen, gridColor, (board_origin[0], y),
                              (board_origin[0] + board_size, y), 3)

        tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    board_origin[0] + j * tile_size,
                    board_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                if (human_can_click and not game_over and
                        board[i][j] == ttt.EMPTY and rect.collidepoint(mouse)):
                    pygame.draw.rect(screen, cellHover, rect.inflate(-8, -8), border_radius=10)

                if board[i][j] != ttt.EMPTY:
                    placed_at = move_times.get((i, j), 0)
                    progress = min(1.0, (now - placed_at) / 0.22) if placed_at else 1.0
                    mark_color = xColor if board[i][j] == ttt.X else oColor
                    draw_mark(screen, rect.center, board[i][j], tile_size * 0.7, mark_color, progress)

                row.append(rect)
            tiles.append(row)

        win_line = winning_cells(board)
        if win_line and win_line != last_win_line:
            last_win_line = win_line
            win_started_at = now
        if not win_line:
            last_win_line = None
            win_started_at = None

        if win_line:
            for i, j in win_line:
                pygame.draw.rect(screen, winFill, tiles[i][j].inflate(-8, -8), border_radius=10)
                mark_color = xColor if board[i][j] == ttt.X else oColor
                draw_mark(screen, tiles[i][j].center, board[i][j], tile_size * 0.7, mark_color)

            lstart = tiles[win_line[0][0]][win_line[0][1]].center
            lend = tiles[win_line[2][0]][win_line[2][1]].center
            lt = ease_out_cubic(min(1.0, (now - win_started_at) / 0.35)) if win_started_at else 1.0
            animated_end = (lerp(lstart[0], lend[0], lt), lerp(lstart[1], lend[1], lt))
            pygame.draw.line(screen, winColor, lstart, animated_end, 6)

        # Title / status text
        if game_over:
            winner = ttt.winner(board)
            if winner is None:
                title_text = "Game Over: Tie"
            elif game_mode == "2P":
                title_text = f"Game Over: {winner} wins"
            else:
                title_text = f"Game Over: {'You win' if winner == user else winner + ' wins'}"
        elif game_mode == "2P":
            title_text = f"{player}'s turn"
        elif user == player:
            title_text = f"Play as {user}"
        else:
            dot_phase = (dot_phase + dt * 4) % 3
            dots = "." * (int(dot_phase) + 1)
            title_text = f"Computer thinking{dots}"
        title_color = white
        title = largeFont.render(title_text, True, title_color)
        screen.blit(title, title.get_rect(center=(width / 2, 60)))

        if game_mode == "AI":
            subText = tinyFont.render(f"Difficulty: {difficulty}", True, faintGray)
        else:
            subText = tinyFont.render("2 Player Mode", True, faintGray)
        screen.blit(subText, subText.get_rect(center=(width / 2, 92)))

        draw_score_bar(width / 2, 118)

        # AI move
        if game_mode == "AI" and user != player and not game_over:
            if ai_turn:
                if ai_move_ready_at is None:
                    ai_move_ready_at = now + 0.45
                elif now >= ai_move_ready_at:
                    move = ttt.ai_move(board, difficulty)
                    board = ttt.result(board, move)
                    move_times[move] = now
                    play_sound(snd_place_x if player == ttt.X else snd_place_o)
                    ai_turn = False
                    ai_move_ready_at = None
            else:
                ai_turn = True

        # Human move (works for both the AI-mode human and either 2P player)
        if clicked and human_can_click and not game_over:
            for i in range(3):
                for j in range(3):
                    if board[i][j] == ttt.EMPTY and tiles[i][j].collidepoint(mouse):
                        placing = player
                        board = ttt.result(board, (i, j))
                        move_times[(i, j)] = now
                        play_sound(snd_place_x if placing == ttt.X else snd_place_o)

        # Score + outcome sound, fired once when the game just ended
        if game_over and not outcome_sound_played:
            winner = ttt.winner(board)
            if winner is None:
                score["Tie"] += 1
                play_sound(snd_tie)
            else:
                score[winner] += 1
                play_sound(snd_win)
            outcome_sound_played = True

        if game_over:
            againButton = pygame.Rect(0, 0, width / 3, 50)
            againButton.center = (width / 2, height - 40)
            hovered = againButton.collidepoint(mouse)
            grown = draw_button(screen, againButton, hovered, dt, key="again", border=accent)
            again = mediumFont.render("Play Again", True, white)
            screen.blit(again, again.get_rect(center=grown.center))

            if clicked and againButton.collidepoint(mouse):
                new_round()
                play_sound(snd_click)

    # -----------------------------------------------------------------
    # Fade-in overlay on every screen change
    # -----------------------------------------------------------------
    if screen_fade > 0:
        screen_fade = max(0.0, screen_fade - dt * 3.2)
        alpha = int(255 * ease_out_cubic(screen_fade))
        if alpha > 0:
            overlay = pygame.Surface(size)
            overlay.fill((10, 10, 14))
            overlay.set_alpha(alpha)
            screen.blit(overlay, (0, 0))

    pygame.display.flip()