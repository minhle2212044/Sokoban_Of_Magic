import time
# Import module helper
import sokoban_helpers as H
from sokoban_helpers import (
    PriorityQueue,     # Hàng đợi ưu tiên
    PosOfPlayer,       # Lấy tọa độ người chơi
    PosOfBoxes,        # Lấy tọa độ các hộp
    PosOfWalls,        # Lấy tọa độ các tường
    PosOfGoals,        # Lấy tọa độ các mục tiêu
    isEndState,        # Kiểm tra trạng thái kết thúc (tất cả hộp ở mục tiêu)
    legalActions,      # Lấy các hành động hợp lệ từ trạng thái hiện tại
    updateState,       # Cập nhật trạng thái sau một hành động
    isFailed,          # Kiểm tra deadlock/trạng thái thất bại (tối ưu hóa)
    transferToGameState, # Chuyển layout map sang GameState (dạng mảng numpy)
)


def heuristic(posPlayer, posBox):
    """
    Hàm Heuristic h(n): Ước lượng chi phí từ trạng thái hiện tại đến mục tiêu.
    Sử dụng tổng khoảng cách Manhattan giữa các hộp và các mục tiêu chưa khớp.
    """
    distance = 0
    # Lấy các hộp đã nằm trên mục tiêu (đã hoàn thành)
    completes = set(H.posGoals) & set(posBox)
    
    # Danh sách các hộp cần di chuyển và các mục tiêu còn lại
    sortposBox = list(set(posBox).difference(completes))
    sortposGoals = list(set(H.posGoals).difference(completes))
    
    # Tính tổng khoảng cách Manhattan
    min_length = min(len(sortposBox), len(sortposGoals))
    for i in range(min_length):
        distance += (abs(sortposBox[i][0] - sortposGoals[i][0])) + \
                    (abs(sortposBox[i][1] - sortposGoals[i][1]))
    
    # Thêm phạt nếu số lượng hộp và mục tiêu không khớp (giúp tăng tính chính xác)
    if len(sortposBox) != len(sortposGoals):
          # Phạt lớn để tránh các đường đi không hợp lý
          distance += 1000 * abs(len(sortposBox) - len(sortposGoals))
    
    return distance


def cost(actions):
    """
    Hàm chi phí g(n): Tổng số lần đẩy hộp (ký tự in hoa) từ trạng thái bắt đầu.
    """
    # Tính chi phí dựa trên số lần đẩy hộp
    return len([x for x in actions if x.isupper()])


def aStarSearch():
    """
    Triển khai lõi thuật toán A* Search.
    Returns: (solution, explored_count)
    """
    beginBox = PosOfBoxes(H.gameState)
    beginPlayer = PosOfPlayer(H.gameState)

    start_state = (beginPlayer, beginBox)
    
    # Frontier: Chứa các trạng thái cần khám phá (sắp xếp theo F-cost)
    frontier = PriorityQueue()
    # Actions: Chứa chuỗi hành động dẫn đến trạng thái tương ứng trong frontier
    actions = PriorityQueue()
    
    # ExploredSet: Chứa các trạng thái đã POP (đã khám phá)
    exploredSet = set()
    
    count = 0 # Số trạng thái đã khám phá (POP)
    
    # Khởi tạo chi phí ban đầu
    initial_g = 0
    initial_h = heuristic(beginPlayer, beginBox)
    initial_f = initial_g + initial_h

    # Push trạng thái bắt đầu vào Frontier và Actions
    frontier.push([start_state], initial_f) 
    actions.push([], initial_f) # Chuỗi hành động ban đầu là rỗng

    
    while not frontier.isEmpty():
        # Lấy trạng thái và chuỗi hành động có F-cost thấp nhất ra khỏi Frontier
        node = frontier.pop()
        node_action = actions.pop()

        current_state = node[-1] 
        current_posPlayer = current_state[0]
        current_posBox = current_state[1]

        # Kiểm tra nếu trạng thái này đã được khám phá VÀ có chi phí tốt hơn
        # (Trong A* này, ta đơn giản chỉ bỏ qua nếu đã POP, đảm bảo không lặp)
        if current_state in exploredSet:
            continue
        
        # Đánh dấu trạng thái là đã khám phá (POP)
        exploredSet.add(current_state)
        count += 1 # Tăng số lượng trạng thái đã khám phá
        
        # KIỂM TRA MỤC TIÊU
        if isEndState(current_posBox):
            solution = ''.join(node_action) 
            print(f"Solution found: {solution}")
            print(f"States explored: {count}")
            return solution, count

        # Tính toán G-cost hiện tại (g(n))
        current_g_cost = cost(node_action) 
        
        # Sinh ra các trạng thái con
        for action in legalActions(current_posPlayer, current_posBox):
            newPosPlayer, newPosBox = updateState(current_posPlayer, current_posBox, action)
            new_state = (newPosPlayer, newPosBox)
            
            # TỐI ƯU HÓA: KIỂM TRA DEADLOCK NGAY LẬP TỨC
            if isFailed(newPosBox):
                continue
            
            # KIỂM TRA TRÙNG LẶP: Nếu trạng thái này đã được khám phá, bỏ qua
            if new_state in exploredSet:
                continue

            # Tính toán chi phí cho trạng thái mới
            new_action_char = action[-1]
            # G'(n): Chi phí mới = Chi phí cũ + Chi phí hành động mới
            new_g_cost = current_g_cost + cost([new_action_char])
            # H'(n): Heuristic mới
            new_h_cost = heuristic(newPosPlayer, newPosBox)
            # F(n) = G(n) + H(n)
            f_cost = new_g_cost + new_h_cost 
            
            # Thêm trạng thái mới vào Frontier và Actions
            frontier.push(node + [new_state], f_cost) 
            actions.push(node_action + [new_action_char], f_cost)

    # Nếu Frontier rỗng mà không tìm thấy lời giải
    print("No solution found")
    return 'x', count


def astar_search(layout, time_limit=1800):
    """
    Hàm wrapper (bao bọc) cho thuật toán A*. 
    Được gọi từ main1.py để khởi tạo trạng thái và giới hạn thời gian.
    """
    time_start = time.time()
    
    # Khởi tạo trạng thái game toàn cục (H.gameState, H.posWalls, H.posGoals)
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    
    # Bắt đầu tìm kiếm lõi
    solution, explored_count = aStarSearch()
    
    time_end = time.time()
    
    # KIỂM TRA TIMEOUT SAU KHI THUẬT TOÁN KẾT THÚC
    if time_end - time_start > time_limit:
        print("Timeout!")
        return 'x', explored_count
    
    return solution, explored_count


def test_astar():
    """Hàm kiểm tra độc lập (dùng cho debug)."""
    try:
        with open("input/1.txt", "r", encoding="utf-8") as f:
            layout = [line.rstrip("\n") for line in f if line.strip() != ""]
        
        solution, count = astar_search(layout)
        print(f"Final A* solution: {solution}, Explored: {count}")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'input/1.txt'. Vui lòng tạo file này để kiểm tra.")


if __name__ == "__main__":
    test_astar()