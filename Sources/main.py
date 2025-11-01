import os
import time
import threading
import numpy as np
import pygame
from pygame.constants import KEYDOWN
import psutil

import astar
import dfs

# ==============================
# CONFIGURATION
# ==============================
ROOT_DIR = os.getcwd()
PATH_BOARD = os.path.join(ROOT_DIR, '..', 'Testcases')
ASSETS_PATH = os.path.join(ROOT_DIR, '..', 'Assets')

# HẰNG SỐ GIỚI HẠN THỜI GIAN
AI_TIME_LIMIT_SECONDS = 10 

# LỚP GIÁM SÁT BỘ NHỚ (THREAD)
class MemoryMonitor(threading.Thread):
    """Theo dõi và ghi lại mức sử dụng RAM tối đa (Max Total RSS) của tiến trình."""
    def __init__(self, pid, interval=0.1):
        super().__init__()
        self.pid = pid
        self.interval = interval
        self.max_rss = 0
        self._stop_event = threading.Event()
        self.daemon = True

    def run(self):
        process = psutil.Process(self.pid)
        while not self._stop_event.is_set():
            try:
                rss_mb = process.memory_info().rss / (1024 * 1024)
                if rss_mb > self.max_rss:
                    self.max_rss = rss_mb
            except psutil.NoSuchProcess:
                break
            time.sleep(self.interval)

    def stop(self):
        """Đặt cờ để dừng luồng giám sát."""
        self._stop_event.set()

    def get_max_memory_usage(self):
        return self.max_rss

# ==============================
# UTILITY FUNCTIONS
# ==============================
def format_row(row):
    """Chuyển đổi ký tự trong map từ định dạng file sang định dạng game."""
    for i in range(len(row)):
        if row[i] == '1':
            row[i] = '#' # Wall
        elif row[i] == 'p':
            row[i] = '@' # Player
        elif row[i] == 'b':
            row[i] = '$' # Box
        elif row[i] == 'c':
            row[i] = '%' # Goal (Check Point)


def get_board(path):
    """Đọc file map và định dạng lại."""
    result = np.loadtxt(path, dtype=str, delimiter=',')
    for row in result:
        format_row(row)
    return result


def get_pair(path):
    """Đọc file tọa độ check point (nếu có)."""
    return np.loadtxt(path, dtype=int, delimiter=',')


def get_boards():
    """Lấy danh sách tất cả các map."""
    return [get_board(os.path.join(PATH_BOARD, f))
            for f in os.listdir(PATH_BOARD) if f.endswith('.txt')]

# ==============================
# INITIAL DATA
# ==============================
maps = get_boards()

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
BLACK = (0, 0, 0)
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
    """Vẽ chữ căn giữa màn hình."""
    font = pygame.font.SysFont(None, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(320, y))
    screen.blit(surf, rect)


def draw_text_left(text, size, color, x, y):
    """Vẽ chữ căn trái."""
    font = pygame.font.SysFont(None, size)
    screen.blit(font.render(text, True, color), (x, y))


def render_map(board):
    """Vẽ trạng thái map lên màn hình."""
    width, height = len(board[0]), len(board)
    indent = (640 - width * 32) / 2.0

    for i in range(height):
        for j in range(width):
            screen.blit(space, (j * 32 + indent, i * 32 + 250))
            cell = board[i][j]
            
            # Vẽ các thành phần dựa trên ký tự map
            if cell == '#':
                screen.blit(wall, (j * 32 + indent, i * 32 + 250))
            elif cell == '$':
                screen.blit(box, (j * 32 + indent, i * 32 + 250))
            elif cell == '%':
                screen.blit(point, (j * 32 + indent, i * 32 + 250))
            elif cell == '@':
                screen.blit(player, (j * 32 + indent, i * 32 + 250))
            
            # Trạng thái kết hợp (Box on Goal, Player on Goal)
            elif cell == 'X':
                screen.blit(point, (j * 32 + indent, i * 32 + 250))
                screen.blit(box, (j * 32 + indent, i * 32 + 250))
            elif cell == '+':
                screen.blit(point, (j * 32 + indent, i * 32 + 250))
                screen.blit(player, (j * 32 + indent, i * 32 + 250))


def draw_progress_bar(x, y, w, h, progress):
    """Vẽ thanh tiến trình cho phần chơi lại."""
    pygame.draw.rect(screen, GREY, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w * progress, h))


# ==============================
# SCENES
# ==============================
def init_game(map, map_number, algorithm):
    """Màn hình khởi tạo/chọn map."""
    draw_text_center('Sokoban of Magic', 60, WHITE, 80)
    draw_text_center('Select your map!!!', 20, WHITE, 140)
    draw_text_center(f"Lv.{map_number + 1}", 30, WHITE, 200)
    screen.blit(arrow_left, (246, 188))
    screen.blit(arrow_right, (370, 188))
    draw_text_center(algorithm, 30, WHITE, 600)
    render_map(map)
    draw_text_center("Press Enter to start | Space to switch AI", 18, WHITE, 620)


def loading_game(elapsed_time):
    """Màn hình loading khi AI đang giải."""
    screen.blit(loading_background, (0, 0))
    draw_text_center('Solving...', 40, WHITE, 60)
    draw_text_center('AI is thinking. Please wait...', 20, WHITE, 100)
    
    # Cảnh báo khi vượt quá giới hạn thời gian
    if elapsed_time > AI_TIME_LIMIT_SECONDS:
        draw_text_center(f"TIME LIMIT EXCEEDED!", 24, (255, 0, 0), 580)
        draw_text_center("Press ESC to cancel search.", 18, WHITE, 620)
    else:
        draw_text_center(f"Elapsed: {elapsed_time:.1f}s", 24, WHITE, 580)


def found_game(map, steps, ai_time, play_time, explored_states, max_memory):
    """Màn hình kết quả khi tìm thấy lời giải."""
    screen.blit(found_background, (0, 0))
    draw_text_center('Problem Solved!', 40, BLACK, 80)
    draw_text_center(f'Steps: {steps} | Explored: {explored_states}', 22, BLACK, 120)
    draw_text_center(f'Algorithm Time: {ai_time:.2f}s | Play Time: {play_time:.2f}s', 22, BLACK, 150)
    draw_text_center(f'Max Total RAM: {max_memory:.2f} MB', 22, BLACK, 180) 
    draw_text_center('Press Enter to continue or ESC to Main Menu', 20, BLACK, 600)
    render_map(map)


def notfound_game(ai_time, explored_states, max_memory):
    """Màn hình kết quả khi không tìm thấy lời giải (bao gồm Timeout)."""
    screen.blit(notfound_background, (0, 0))
    
    # Hiển thị thông báo Timeout nếu thời gian chạy gần bằng hoặc vượt quá giới hạn
    if ai_time >= AI_TIME_LIMIT_SECONDS:
        title = 'TIME LIMIT REACHED!'
    else:
        title = 'Oh no, no solution found!'
        
    draw_text_center(title, 40, BLACK, 100)
    draw_text_center(f"Algorithm ran {ai_time:.2f}s | Explored: {explored_states}", 22, BLACK, 140)
    draw_text_center(f"Max Total RAM: {max_memory:.2f} MB", 22, BLACK, 170) 
    draw_text_center('Press Enter to retry or ESC to Main Menu', 20, BLACK, 600)


# ==============================
# MAIN GAME LOOP
# ==============================
def sokoban():
    """Vòng lặp chính của trò chơi."""
    running = True
    scene_state = "init"
    map_number = 0
    algorithm = "A Star Search"
    list_board = []
    found = True
    ai_runtime = 0
    ai_explored_states = 0
    ai_max_memory = 0
    play_time = 0
    ai_thread = None
    ai_done = False
    ai_start_time = None
    state_length = 0
    current_state = 0
    start_play_time = 0
    paused = False 

    def run_ai():
        """Hàm chạy AI trong luồng riêng. Hàm này chặn luồng chính cho đến khi hoàn thành."""
        nonlocal list_board, ai_runtime, ai_done, found, ai_explored_states, ai_max_memory
        
        pid = os.getpid()
        
        # Bắt đầu giám sát bộ nhớ
        monitor = MemoryMonitor(pid)
        monitor.start()
        
        t0 = time.time()
        
        map_layout = [''.join(row) for row in maps[map_number]]
        
        # GỌI THUẬT TOÁN VÀ TRUYỀN GIỚI HẠN THỜI GIAN
        if algorithm == "A Star Search":
            solution, explored_count = astar.astar_search(map_layout, time_limit=AI_TIME_LIMIT_SECONDS)
        else:
            solution, explored_count = dfs.dfs_search(map_layout, time_limit=AI_TIME_LIMIT_SECONDS)
            
        # Dừng giám sát bộ nhớ
        monitor.stop()
        monitor.join()
        
        final_max_rss = monitor.get_max_memory_usage()
        
        # Tính toán kết quả
        ai_runtime = time.time() - t0
        ai_explored_states = explored_count
        ai_max_memory = final_max_rss # Lưu Max Total RAM
        
        print(f"AI Max Memory Usage: {ai_max_memory:.2f} MB")
        print(f"AI Runtime: {ai_runtime:.2f} seconds")

        # Xử lý kết quả solution
        if solution and solution != 'x':
            try:
                from sokoban_helpers import applyActionSequence
                snapshots = applyActionSequence(map_layout, solution)
                
                board_sequence = []
                for snapshot in snapshots:
                    board_str = snapshot[1]
                    board_lines = board_str.split('\n')
                    board_2d = [list(line) for line in board_lines if line] 
                    board_sequence.append(board_2d)
                    
                list_board = [board_sequence]
                found = True
            except:
                list_board = None
                found = False
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
            # Màn hình kết quả
            if found:
                found_game(list_board[0][state_length - 1], state_length, ai_runtime, play_time, ai_explored_states, ai_max_memory)
            else:
                notfound_game(ai_runtime, ai_explored_states, ai_max_memory)

        # ======================
        # EVENTS
        # ======================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == KEYDOWN:
                if scene_state == "init":
                    # ... (Chọn map và thuật toán) ...
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
                        ai_explored_states = 0
                        ai_max_memory = 0
                        ai_start_time = time.time()
                        
                        # Khởi động AI trong luồng mới
                        ai_thread = threading.Thread(target=run_ai)
                        ai_thread.start()
                        scene_state = "loading"

                elif scene_state == "playing":
                    # ... (Xử lý Pause/Exit) ...
                    if event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        scene_state = "init"

                elif scene_state == "end":
                    # ... (Xử lý quay lại Init) ...
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