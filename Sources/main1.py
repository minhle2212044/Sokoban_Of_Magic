import os
import time
import threading
import numpy as np
import pygame
from pygame.constants import KEYDOWN

import astar
import dfs

# ==============================
# CONFIGURATION
# ==============================
ROOT_DIR = os.getcwd()
PATH_BOARD = os.path.join(ROOT_DIR, '..', 'Testcases')
PATH_CHECKPOINT = os.path.join(ROOT_DIR, '..', 'Checkpoints')
ASSETS_PATH = os.path.join(ROOT_DIR, '..', 'Assets')

# ==============================
# UTILITY FUNCTIONS
# ==============================
def format_row(row):
    for i in range(len(row)):
        if row[i] == '1':
            row[i] = '#'
        elif row[i] == 'p':
            row[i] = '@'
        elif row[i] == 'b':
            row[i] = '$'
        elif row[i] == 'c':
            row[i] = '%'


def get_board(path):
    result = np.loadtxt(path, dtype=str, delimiter=',')
    for row in result:
        format_row(row)
    return result


def get_pair(path):
    return np.loadtxt(path, dtype=int, delimiter=',')


def get_boards():
    return [get_board(os.path.join(PATH_BOARD, f))
            for f in os.listdir(PATH_BOARD) if f.endswith('.txt')]


def get_check_points():
    return [get_pair(os.path.join(PATH_CHECKPOINT, f))
            for f in os.listdir(PATH_CHECKPOINT) if f.endswith('.txt')]


# ==============================
# INITIAL DATA
# ==============================
maps = get_boards()
check_points = get_check_points()

# ==============================
# PYGAME SETUP
# ==============================
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((640, 640))
pygame.display.set_caption('Sokoban of Magic')
clock = pygame.time.Clock()

# COLORS
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREY = (80, 80, 80)

# LOAD ASSETS
os.chdir(ASSETS_PATH)
player = pygame.image.load('wizard.png')
wall = pygame.image.load('wall2.png')
box = pygame.image.load('stone.png')
point = pygame.image.load('circle.png')
space = pygame.image.load('space.png')
arrow_left = pygame.image.load('arrow_left.png')
arrow_right = pygame.image.load('arrow_right.png')

init_background = pygame.image.load('background1.png')
loading_background = pygame.image.load('loading1.png')
notfound_background = pygame.image.load('notfound1.png')
found_background = pygame.image.load('background1.png')

# ==============================
# DRAW HELPERS
# ==============================
def draw_text_center(text, size, color, y):
    font = pygame.font.SysFont(None, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(320, y))
    screen.blit(surf, rect)


def draw_text_left(text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    screen.blit(font.render(text, True, color), (x, y))


def render_map(board):
    width, height = len(board[0]), len(board)
    indent = (640 - width * 32) / 2.0

    for i in range(height):
        for j in range(width):
            screen.blit(space, (j * 32 + indent, i * 32 + 250))
            cell = board[i][j]
            
            if cell == '#':
                screen.blit(wall, (j * 32 + indent, i * 32 + 250))
            elif cell == '$':
                screen.blit(box, (j * 32 + indent, i * 32 + 250))
            elif cell == '%':
                screen.blit(point, (j * 32 + indent, i * 32 + 250))
            elif cell == '@':
                screen.blit(player, (j * 32 + indent, i * 32 + 250))
            
            # ----- ADD THESE TWO NEW CASES -----
            elif cell == 'X': # 'X' = Box on Goal
                screen.blit(point, (j * 32 + indent, i * 32 + 250)) # Draw goal
                screen.blit(box, (j * 32 + indent, i * 32 + 250))   # Draw box on top
            elif cell == '+': # '+' = Player on Goal
                screen.blit(point, (j * 32 + indent, i * 32 + 250)) # Draw goal
                screen.blit(player, (j * 32 + indent, i * 32 + 250)) # Draw player on top
            # -------------------------------------


def draw_progress_bar(x, y, w, h, progress):
    pygame.draw.rect(screen, GREY, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w * progress, h))


# ==============================
# SCENES
# ==============================
def init_game(map, map_number, algorithm):
    draw_text_center('Sokoban of Magic', 60, WHITE, 80)
    draw_text_center('Select your map!!!', 20, WHITE, 140)
    draw_text_center(f"Lv.{map_number + 1}", 30, WHITE, 200)
    screen.blit(arrow_left, (246, 188))
    screen.blit(arrow_right, (370, 188))
    draw_text_center(algorithm, 30, WHITE, 600)
    render_map(map)
    draw_text_center("Press Enter to start | Space to switch AI", 18, WHITE, 620)


def loading_game(elapsed_time):
    screen.blit(loading_background, (0, 0))
    draw_text_center('Solving...', 40, WHITE, 60)
    draw_text_center('AI is thinking. Please wait...', 20, WHITE, 100)
    draw_text_center(f"Elapsed: {elapsed_time:.1f}s", 24, WHITE, 580)


def found_game(map, steps, ai_time, play_time):
    screen.blit(found_background, (0, 0))
    draw_text_center('🎉 Problem Solved!', 40, WHITE, 80)
    draw_text_center(f'Steps: {steps}', 22, WHITE, 120)
    draw_text_center(f'Algorithm: {ai_time:.2f}s | Play: {play_time:.2f}s', 22, WHITE, 150)
    draw_text_center('Press Enter to continue or ESC to Main Menu', 20, WHITE, 600)
    render_map(map)


def notfound_game(ai_time):
    screen.blit(notfound_background, (0, 0))
    draw_text_center('Oh no, no solution found!', 40, WHITE, 100)
    draw_text_center(f"Algorithm ran {ai_time:.2f}s with no result", 22, WHITE, 140)
    draw_text_center('Press Enter to retry or ESC to Main Menu', 20, WHITE, 600)


# ==============================
# MAIN GAME LOOP
# ==============================
def sokoban():
    running = True
    scene_state = "init"
    map_number = 0
    algorithm = "A Star Search"
    list_board = []
    found = True
    ai_runtime = 0
    play_time = 0
    ai_thread = None
    ai_done = False
    ai_start_time = None
    state_length = 0
    current_state = 0
    start_play_time = 0
    paused = False  # thêm trạng thái tạm dừng

    def run_ai():
        """Hàm chạy AI trong luồng riêng."""
        nonlocal list_board, ai_runtime, ai_done, found
        list_check_point = check_points[map_number]
        t0 = time.time()
        
        # Convert map to string format for algorithms
        map_layout = []
        for row in maps[map_number]:
            map_layout.append(''.join(row))
        
        if algorithm == "A Star Search":
            solution = astar.astar_search(map_layout)
        else:  # Depth First Search
            solution = dfs.dfs_search(map_layout)
            
        ai_runtime = time.time() - t0
        
        if solution and solution != 'x':
            # Convert solution to board sequence using helper function
            from sokoban_helpers import applyActionSequence
            snapshots = applyActionSequence(map_layout, solution)
            # Convert snapshots to the format expected by main.py
            # Each snapshot is [title, board_str, separator], we need board_str
            board_sequence = []
            for snapshot in snapshots:
                board_str = snapshot[1]  # Get the board string
                # Convert string to 2D array
                board_lines = board_str.split('\n')
                board_2d = [list(line) for line in board_lines]
                board_sequence.append(board_2d)
            list_board = [board_sequence]
            found = True
        else:
            list_board = None
            found = False
            
        ai_done = True

    while running:
        screen.blit(init_background, (0, 0))

        if scene_state == "init":
            init_game(maps[map_number], map_number, algorithm)

        elif scene_state == "loading":
            elapsed = time.time() - ai_start_time
            loading_game(elapsed)
            if ai_done:
                if found:
                    scene_state = "playing"
                    state_length = len(list_board[0])
                    current_state = 0
                    start_play_time = time.time()
                else:
                    scene_state = "end"

        elif scene_state == "playing":
            if not paused:
                play_time = time.time() - start_play_time
                progress = current_state / state_length if state_length else 0
                clock.tick(3)

                render_map(list_board[0][current_state])
                draw_progress_bar(120, 220, 400, 15, progress)
                draw_text_left(f"Step: {current_state + 1}/{state_length}", 20, WHITE, 20, 20)
                draw_text_left(f"Play Time: {play_time:.1f}s", 20, WHITE, 450, 20)
                draw_text_center("Press P to Pause | ESC to Exit", 18, WHITE, 600)

                current_state += 1
                if current_state >= state_length:
                    scene_state = "end"
            else:
                draw_text_center("⏸ PAUSED - Press P to Resume | ESC to Main Menu", 22, WHITE, 320)
                render_map(list_board[0][current_state - 1])

        elif scene_state == "end":
            if found:
                found_game(list_board[0][state_length - 1], state_length, ai_runtime, play_time)
            else:
                notfound_game(ai_runtime)

        # ======================
        # EVENTS
        # ======================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == KEYDOWN:
                if scene_state == "init":
                    if event.key == pygame.K_RIGHT and map_number < len(maps) - 1:
                        map_number += 1
                    elif event.key == pygame.K_LEFT and map_number > 0:
                        map_number -= 1
                    elif event.key == pygame.K_SPACE:
                        if algorithm == "A Star Search":
                            algorithm = "Depth First Search"
                        else:
                            algorithm = "A Star Search"
                    elif event.key == pygame.K_RETURN:
                        ai_done = False
                        ai_thread = threading.Thread(target=run_ai)
                        ai_thread.start()
                        ai_start_time = time.time()
                        scene_state = "loading"

                elif scene_state == "playing":
                    if event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        scene_state = "init"

                elif scene_state == "end":
                    if event.key == pygame.K_RETURN:
                        scene_state = "init"
                    elif event.key == pygame.K_ESCAPE:
                        scene_state = "init"

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    sokoban()