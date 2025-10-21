import numpy as np


gameState = ''
posWalls = ''
posGoals = ''


class PriorityQueue:
    def  __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        PriorityQueue.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = PriorityQueue.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0

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
    return tuple(np.argwhere(gs == 2)[0])


def PosOfBoxes(gs):
    return tuple(tuple(x) for x in np.argwhere((gs == 3) | (gs == 5)))


def PosOfWalls(gs):
    return tuple(tuple(x) for x in np.argwhere(gs == 1))


def PosOfGoals(gs):
    return tuple(tuple(x) for x in np.argwhere((gs == 4) | (gs == 5)))


def isEndState(posBox):
    return sorted(posBox) == sorted(posGoals)


def isLegalAction(action, posPlayer, posBox):
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls


def legalActions(posPlayer, posBox):
    allActions = [[-1,0,'u','U'],[1,0,'d','D'],[0,-1,'l','L'],[0,1,'r','R']]
    xPlayer, yPlayer = posPlayer
    legalActionsList = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox:
            action.pop(2)
        else:
            action.pop(3)
        if isLegalAction(action, posPlayer, posBox):
            legalActionsList.append(action)
        else:
            continue
    return tuple(tuple(x) for x in legalActionsList)


def updateState(posPlayer, posBox, action):
    xPlayer, yPlayer = posPlayer
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]]
    posBoxList = [list(x) for x in posBox]
    if action[-1].isupper():
        posBoxList.remove(newPosPlayer)
        posBoxList.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    newPosBox = tuple(tuple(x) for x in posBoxList)
    return tuple(newPosPlayer), newPosBox


def isFailed(posBox):
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
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1),
                    (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1),
                    (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
    return False


def transferToGameState(layout):
    # Input format is already comma-separated, so we just need to split each line
    layout = [line.split(",") for line in layout if line.strip()]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ' or layout[irow][icol] == '': layout[irow][icol] = 0
            elif layout[irow][icol] == '#' or layout[irow][icol] == '1': layout[irow][icol] = 1
            elif layout[irow][icol] == '&' or layout[irow][icol] == 'p': layout[irow][icol] = 2
            elif layout[irow][icol] == 'B' or layout[irow][icol] == 'b': layout[irow][icol] = 3
            elif layout[irow][icol] == '.' or layout[irow][icol] == 'c': layout[irow][icol] = 4
            elif layout[irow][icol] == 'X': layout[irow][icol] = 5  # Box on goal position
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)])
    return np.array(layout, dtype=int)


def printBoard(gs, posPlayer, posBox):
    display = []
    rows, cols = gs.shape
    for i in range(rows):
        row = ""
        for j in range(cols):
            cell = " "
            if (i, j) in posWalls:
                cell = "#"
            elif (i, j) in posBox and (i, j) in posGoals:
                cell = "X"
            elif (i, j) in posBox:
                cell = "B"
            elif (i, j) in posGoals:
                cell = "."
            if (i, j) == posPlayer:
                cell = "&"
            row += cell
        display.append(row)
    return "\n".join(display), cols


def applyActionSequence(layout, solution):
    state = transferToGameState(layout)
    posPlayer = PosOfPlayer(state)
    posBox = PosOfBoxes(state)

    snapshots = []
    board_str, cols = printBoard(state, posPlayer, posBox)
    snapshots.append(["Bắt đầu:", board_str, "=" * cols])

    move_map = {
        'u': (-1, 0), 'U': (-1, 0),
        'd': (1, 0), 'D': (1, 0),
        'l': (0, -1), 'L': (0, -1),
        'r': (0, 1), 'R': (0, 1),
    }

    for i, act in enumerate(solution):
        dx, dy = move_map[act]
        newPosPlayer = (posPlayer[0] + dx, posPlayer[1] + dy)
        newPosBox = list(posBox)
        if act.isupper() and newPosPlayer in posBox:
            box_index = newPosBox.index(newPosPlayer)
            newPosBox[box_index] = (newPosPlayer[0] + dx, newPosPlayer[1] + dy)
        posPlayer = newPosPlayer
        posBox = tuple(newPosBox)
        board_str, cols = printBoard(state, posPlayer, posBox)
        snapshots.append([f"Bước {i+1}: {act}", board_str, "=" * cols])

    return snapshots


