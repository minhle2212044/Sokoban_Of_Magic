import numpy as np # Import thư viện NumPy

# Khai báo các biến toàn cục (Global state)
gameState = ''  # Ma trận trạng thái game (dạng numpy array)
posWalls = ''   # Tọa độ các bức tường
posGoals = ''   # Tọa độ các mục tiêu


class PriorityQueue:
    """Triển khai Hàng đợi ưu tiên (Priority Queue) cho thuật toán A*."""
    def __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        """Thêm phần tử vào hàng đợi dựa trên độ ưu tiên (priority)."""
        entry = (priority, self.Count, item)
        PriorityQueue.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        """Lấy phần tử có độ ưu tiên cao nhất (priority nhỏ nhất)."""
        (_, _, item) = PriorityQueue.heappop(self.Heap)
        return item

    def isEmpty(self):
        """Kiểm tra xem hàng đợi có rỗng không."""
        return len(self.Heap) == 0

    # Các hàm heappush, heappop, _siftup, _siftdown là các hàm nội bộ 
    # quản lý cấu trúc Heap (cây nhị phân)
    @staticmethod
    def heappush(heap, item):
        heap.append(item)
        PriorityQueue._siftdown(heap, 0, len(heap)-1)

    @staticmethod
    def heappop(heap):
        lastelt = heap.pop()
        if heap:
            returnitem = heap[0]
            heap[0] = lastelt
            PriorityQueue._siftup(heap, 0)
            return returnitem
        return lastelt

    @staticmethod
    def _siftup(heap, pos):
        endpos = len(heap)
        startpos = pos
        newitem = heap[pos]
        childpos = 2*pos + 1
        while childpos < endpos:
            rightpos = childpos + 1
            if rightpos < endpos and not heap[childpos] < heap[rightpos]:
                childpos = rightpos
            heap[pos] = heap[childpos]
            pos = childpos
            childpos = 2*pos + 1
        heap[pos] = newitem
        PriorityQueue._siftdown(heap, startpos, pos)

    @staticmethod
    def _siftdown(heap, startpos, pos):
        newitem = heap[pos]
        while pos > startpos:
            parentpos = (pos - 1) >> 1
            parent = heap[parentpos]
            if newitem < parent:
                heap[pos] = parent
                pos = parentpos
                continue
            break
        heap[pos] = newitem


def PosOfPlayer(gs):
    """Tìm và trả về tọa độ của người chơi."""
    # Giá trị 2 đại diện cho người chơi trong mảng trạng thái
    return tuple(np.argwhere(gs == 2)[0])


def PosOfBoxes(gs):
    """Tìm và trả về tọa độ của tất cả các hộp (kể cả hộp trên mục tiêu)."""
    # Giá trị 3 (Box) và 5 (Box on Goal)
    return tuple(tuple(x) for x in np.argwhere((gs == 3) | (gs == 5)))


def PosOfWalls(gs):
    """Tìm và trả về tọa độ của tất cả các bức tường."""
    # Giá trị 1 (Wall)
    return tuple(tuple(x) for x in np.argwhere(gs == 1))


def PosOfGoals(gs):
    """Tìm và trả về tọa độ của tất cả các mục tiêu (kể cả mục tiêu có hộp)."""
    # Giá trị 4 (Goal) và 5 (Box on Goal)
    return tuple(tuple(x) for x in np.argwhere((gs == 4) | (gs == 5)))


def isEndState(posBox):
    """Kiểm tra xem trạng thái hiện tại có phải là trạng thái chiến thắng không."""
    # Trạng thái chiến thắng: Tập hợp vị trí hộp bằng tập hợp vị trí mục tiêu
    return sorted(posBox) == sorted(posGoals)


def isLegalAction(action, posPlayer, posBox):
    """Kiểm tra tính hợp lệ của hành động tiếp theo."""
    xPlayer, yPlayer = posPlayer
    # Nếu là hành động đẩy hộp (chữ hoa)
    if action[-1].isupper():
        # Tọa độ vị trí sau khi đẩy hộp (2 bước)
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        # Tọa độ vị trí người chơi sau khi di chuyển (1 bước)
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        
    # Hành động hợp lệ nếu vị trí cuối không phải là hộp hoặc tường (đã kiểm tra trong legalActions)
    # Và không phải là tường
    return (x1, y1) not in posBox + posWalls


def legalActions(posPlayer, posBox):
    """Tạo danh sách các hành động hợp lệ (di chuyển hoặc đẩy) từ trạng thái hiện tại."""
    # Các hành động cơ bản: [[dx, dy, move_char (người), push_char (đẩy)]]
    allActions = [[-1,0,'u','U'],[1,0,'d','D'],[0,-1,'l','L'],[0,1,'r','R']]
    xPlayer, yPlayer = posPlayer
    legalActionsList = []
    
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        
        # Nếu vị trí tiếp theo có hộp:
        if (x1, y1) in posBox:
            action.pop(2) # Loại bỏ ký tự di chuyển thường (chỉ còn đẩy)
        else:
            action.pop(3) # Loại bỏ ký tự đẩy (chỉ còn di chuyển thường)
            
        # Kiểm tra hành động cuối cùng có hợp lệ không (ví dụ: đẩy hộp vào tường/hộp khác)
        if isLegalAction(action, posPlayer, posBox):
            legalActionsList.append(action)
        else:
            continue
            
    return tuple(tuple(x) for x in legalActionsList)


def updateState(posPlayer, posBox, action):
    """Cập nhật vị trí người chơi và hộp sau khi thực hiện một hành động."""
    xPlayer, yPlayer = posPlayer
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]]
    posBoxList = [list(x) for x in posBox]
    
    # Nếu là hành động đẩy hộp (chữ hoa)
    if action[-1].isupper():
        # Loại bỏ vị trí hộp cũ
        posBoxList.remove(newPosPlayer)
        # Thêm vị trí hộp mới (đẩy thêm 1 bước)
        posBoxList.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
        
    newPosBox = tuple(tuple(x) for x in posBoxList)
    
    return tuple(newPosPlayer), newPosBox


def isFailed(posBox):
    """
    Kiểm tra Deadlock (tối ưu hóa). 
    Phát hiện các trường hợp hộp bị kẹt vào góc/tường mà không nằm trên mục tiêu.
    """
    # Các pattern xoay và lật để kiểm tra 9 ô xung quanh hộp
    rotatePattern = [[0,1,2,3,4,5,6,7,8],
                     [2,5,8,1,4,7,0,3,6],
                     [0,1,2,3,4,5,6,7,8][::-1],
                     [2,5,8,1,4,7,0,3,6][::-1]]
    flipPattern = [[2,1,0,5,4,3,8,7,6],
                     [0,3,6,1,4,7,2,5,8],
                     [2,1,0,5,4,3,8,7,6][::-1],
                     [0,3,6,1,4,7,2,5,8][::-1]]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        # Chỉ kiểm tra hộp không nằm trên mục tiêu
        if box not in posGoals:
            # Tạo tọa độ 9 ô xung quanh hộp
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1),
                     (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1),
                     (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                # Kiểm tra các mẫu Deadlock (Ví dụ: kẹt giữa tường, kẹt giữa tường và hộp)
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True
                # Trường hợp Deadlock phức tạp hơn
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
                
    return False


def transferToGameState(layout):
    """Chuyển đổi layout map dạng list of strings sang ma trận numpy (GameState)."""
    processed_layout = []
    
    # Tự động phát hiện định dạng layout (có dấu phẩy hoặc không)
    if layout and ',' in layout[0]:
        for line in layout:
            if line.strip():
                processed_layout.append([cell.strip() for cell in line.split(',')])
    else:
        for line in layout:
            if line.strip():
                processed_layout.append(list(line))

    layout = processed_layout
    if not layout:
        return np.array([], dtype=int)

    # Chuyển đổi ký tự sang số (mapping)
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            cell = str(layout[irow][icol]).strip()

            if cell == ' ' or cell == '': layout[irow][icol] = 0   # 0 = Space
            elif cell == '#' or cell == '1': layout[irow][icol] = 1 # 1 = Wall
            elif cell == '@' or cell == '&' or cell == 'p': layout[irow][icol] = 2 # 2 = Player
            elif cell == '$' or cell == 'B' or cell == 'b': layout[irow][icol] = 3 # 3 = Box
            elif cell == '%' or cell == '.' or cell == 'c': layout[irow][icol] = 4 # 4 = Goal
            elif cell == 'X': layout[irow][icol] = 5 # 5 = Box on Goal
            elif cell == '+': layout[irow][icol] = 2 # 2 = Player on Goal (xử lý như Player)
            else: layout[irow][icol] = 0 
        
        # Đệm thêm tường nếu hàng thiếu
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)])

    return np.array(layout, dtype=int)


def printBoard(gs, posPlayer, posBox):
    """Tạo lại chuỗi biểu diễn map (string representation) từ GameState."""
    display = []
    rows, cols = gs.shape
    for i in range(rows):
        row = ""
        for j in range(cols):
            cell = " " 
            
            is_wall = (i, j) in posWalls
            is_goal = (i, j) in posGoals
            is_box = (i, j) in posBox
            is_player = (i, j) == posPlayer

            # Xử lý theo thứ tự lớp phủ (layer)
            if is_wall: cell = "#"
            elif is_box and is_goal: cell = "X"
            elif is_player and is_goal: cell = "+"
            elif is_box: cell = "$"
            elif is_player: cell = "@"
            elif is_goal: cell = "%"
            
            row += cell
        display.append(row)
    return "\n".join(display), cols


def applyActionSequence(layout, solution):
    """
    Tạo một chuỗi các snapshot (trạng thái map) từ chuỗi hành động đã tìm thấy.
    Được sử dụng trong main1.py để tạo hoạt ảnh (animation).
    """
    # Khởi tạo trạng thái
    state = transferToGameState(layout)
    posPlayer = PosOfPlayer(state)
    posBox = PosOfBoxes(state)
    
    snapshots = []
    board_str, cols = printBoard(state, posPlayer, posBox)
    snapshots.append(["Bắt đầu:", board_str, "=" * cols])

    # Mapping ký tự hành động sang tọa độ dịch chuyển
    move_map = {
        'u': (-1, 0), 'U': (-1, 0),
        'd': (1, 0), 'D': (1, 0),
        'l': (0, -1), 'L': (0, -1),
        'r': (0, 1), 'R': (0, 1),
    }

    for i, act in enumerate(solution):
        dx, dy = move_map[act]
        # Vị trí mới của người chơi
        newPosPlayer = (posPlayer[0] + dx, posPlayer[1] + dy)
        newPosBox = list(posBox)
        
        # Nếu là đẩy hộp (chữ hoa)
        if act.isupper() and newPosPlayer in posBox:
            box_index = newPosBox.index(newPosPlayer)
            # Cập nhật vị trí hộp (đẩy thêm 1 bước)
            newPosBox[box_index] = (newPosPlayer[0] + dx, newPosPlayer[1] + dy)
            
        posPlayer = newPosPlayer
        posBox = tuple(newPosBox)
        
        # Ghi lại trạng thái mới
        board_str, cols = printBoard(state, posPlayer, posBox)
        snapshots.append([f"Bước {i+1}: {act}", board_str, "=" * cols])

    return snapshots