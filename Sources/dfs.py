import time
# Import module helper (đã được đặt tên là H)
import sokoban_helpers as H
from sokoban_helpers import (
    PosOfPlayer,       # Lấy tọa độ người chơi
    PosOfBoxes,        # Lấy tọa độ các hộp
    PosOfWalls,        # Lấy tọa độ các tường
    PosOfGoals,        # Lấy tọa độ các mục tiêu
    isEndState,        # Kiểm tra trạng thái kết thúc
    legalActions,      # Lấy các hành động hợp lệ
    updateState,       # Cập nhật trạng thái mới
    isFailed,          # Kiểm tra Deadlock/trạng thái thất bại (Tối ưu hóa)
    transferToGameState, # Chuyển layout map sang GameState
)


def dfsSearch():
    """
    Triển khai lõi thuật toán DFS (Depth-First Search) dạng Graph Search.
    Tích hợp tối ưu hóa Deadlock và lọc trạng thái đã thăm.
    Returns: (solution, explored_count)
    """
    beginBox = PosOfBoxes(H.gameState)
    beginPlayer = PosOfPlayer(H.gameState)
    
    # Kiểm tra nếu đã giải ngay từ đầu
    if isEndState(beginBox):
        print("Already solved!")
        return "", 0
    
    # Stack: Chứa các trạng thái cần khám phá (DFS sử dụng LIFO)
    stack = [(beginPlayer, beginBox, "")]  # Format: (vị trí_người, vị trí_hộp, hành động_đã_thực_hiện)
    exploredSet = set() # Set để lưu trữ các trạng thái đã thăm (lọc trùng lặp)
    count = 0 # Số trạng thái duy nhất được khám phá
    
    # Khởi tạo trạng thái đầu tiên
    startStateKey = (beginPlayer, beginBox)
    exploredSet.add(startStateKey)
    count += 1
    
    while stack:
        # Lấy trạng thái mới nhất ra khỏi stack (đi sâu hơn)
        posPlayer, posBox, actions = stack.pop()
        
        # KIỂM TRA MỤC TIÊU
        if isEndState(posBox):
            solution = actions
            print(f"Solution found: {solution}")
            print(f"States explored: {count}")
            return solution, count
        
        # Sinh ra các trạng thái con
        for action in legalActions(posPlayer, posBox):
            # Tính toán trạng thái mới sau khi thực hiện hành động
            newPosPlayer, newPosBox = updateState(posPlayer, posBox, action)
            
            newStateKey = (newPosPlayer, newPosBox)
            
            # 1. TỐI ƯU HÓA: LOẠI TRỪ DEADLOCK
            # Nếu trạng thái mới dẫn đến deadlock (hộp bị kẹt), bỏ qua nhánh này
            if isFailed(newPosBox): 
                continue
                
            # 2. TỐI ƯU HÓA: LOẠI TRỪ TRẠNG THÁI ĐÃ THĂM
            # Nếu trạng thái (vị trí người và hộp) đã được khám phá, bỏ qua
            if newStateKey in exploredSet:
                continue
            
            # 3. ĐẾM VÀ GHI NHẬN TRẠNG THÁI MỚI
            exploredSet.add(newStateKey)
            count += 1
            
            # Thêm trạng thái mới vào Stack
            newActions = actions + action[-1] # Nối thêm ký tự hành động (u/d/l/r/U/D/L/R)
            stack.append((newPosPlayer, newPosBox, newActions)) 
    
    # Nếu Stack rỗng mà không tìm thấy lời giải
    print("No solution found")
    return 'x', count


def dfs_search(layout, time_limit=1200):
    """
    Hàm wrapper (bao bọc) cho thuật toán DFS. 
    Khởi tạo trạng thái và giới hạn thời gian.
    """
    time_start = time.time()
    
    # Khởi tạo trạng thái game toàn cục (H.gameState, H.posWalls, H.posGoals)
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    
    # Bắt đầu tìm kiếm lõi
    solution, explored_count = dfsSearch()
    
    time_end = time.time()
    
    # KIỂM TRA TIMEOUT SAU KHI THUẬT TOÁN KẾT THÚC
    if time_end - time_start > time_limit:
        print("Timeout!")
        # Trả về 'x' để báo hiệu thất bại (timeout)
        return 'x', explored_count
    
    return solution, explored_count


def test_dfs():
    """Hàm kiểm tra độc lập (dùng cho debug)."""
    try:
        with open("input/1.txt", "r", encoding="utf-8") as f:
            layout = [line.rstrip("\n") for line in f if line.strip() != ""]
        
        solution, count = dfs_search(layout)
        print(f"Final DFS solution: {solution}, Explored: {count}")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'input/1.txt'. Vui lòng tạo file này để kiểm tra.")


if __name__ == "__main__":
    test_dfs()