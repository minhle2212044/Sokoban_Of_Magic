import time
import sokoban_helpers as H
from sokoban_helpers import (
    PriorityQueue,
    PosOfPlayer,
    PosOfBoxes,
    PosOfWalls,
    PosOfGoals,
    isEndState,
    legalActions,
    updateState,
    isFailed,
    transferToGameState,
)


def heuristic(posPlayer, posBox):
    distance = 0
    completes = set(H.posGoals) & set(posBox)
    sortposBox = list(set(posBox).difference(completes))
    sortposGoals = list(set(H.posGoals).difference(completes))
    
    min_length = min(len(sortposBox), len(sortposGoals))
    for i in range(min_length):
        distance += (abs(sortposBox[i][0] - sortposGoals[i][0])) + \
                    (abs(sortposBox[i][1] - sortposGoals[i][1]))
    
    if len(sortposBox) != len(sortposGoals):
         distance += 1000 * abs(len(sortposBox) - len(sortposGoals))
    
    return distance


def cost(actions):
    return len([x for x in actions if x.isupper()])


def aStarSearch():
    beginBox = PosOfBoxes(H.gameState)
    beginPlayer = PosOfPlayer(H.gameState)

    start_state = (beginPlayer, beginBox)
    frontier = PriorityQueue()
    actions = PriorityQueue()
    
    exploredSet = set()
    
    count = 0
    initial_g = 0
    initial_h = heuristic(beginPlayer, beginBox)
    initial_f = initial_g + initial_h

    frontier.push([start_state], initial_f) 
    actions.push([], initial_f)

    
    while not frontier.isEmpty():
        node = frontier.pop()
        node_action = actions.pop()

        current_state = node[-1] 
        current_posPlayer = current_state[0]
        current_posBox = current_state[1]

        if current_state in exploredSet:
             continue
        
        exploredSet.add(current_state)
        count += 1

        if isEndState(current_posBox):
            solution = ''.join(node_action) 
            print(f"Solution found: {solution}")
            print(f"States explored: {count}")
            return solution, count

        current_g_cost = cost(node_action) 
        
        for action in legalActions(current_posPlayer, current_posBox):
            newPosPlayer, newPosBox = updateState(current_posPlayer, current_posBox, action)
            new_state = (newPosPlayer, newPosBox)
            
            if isFailed(newPosBox):
                continue
            
            if new_state in exploredSet:
                continue

            new_action_char = action[-1]
            new_g_cost = current_g_cost + cost([new_action_char])
            new_h_cost = heuristic(newPosPlayer, newPosBox)
            f_cost = new_g_cost + new_h_cost # f(n) = g(n) + h(n)
            
            frontier.push(node + [new_state], f_cost) 
            actions.push(node_action + [new_action_char], f_cost)

    print("No solution found")
    return 'x', count


def astar_search(layout, time_limit=1800):
    """
    A* search wrapper function for main.py integration
    """
    time_start = time.time()
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    
    solution, explored_count = aStarSearch()
    
    time_end = time.time()
    if time_end - time_start > time_limit:
        print("Timeout!")
        return 'x', explored_count
    return solution, explored_count


def test_astar():
    """Test function"""
    try:
        with open("input/1.txt", "r", encoding="utf-8") as f:
            layout = [line.rstrip("\n") for line in f if line.strip() != ""]
        
        solution, count = astar_search(layout)
        print(f"Final A* solution: {solution}, Explored: {count}")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'input/1.txt'. Vui lòng tạo file này để kiểm tra.")


if __name__ == "__main__":
    test_astar()