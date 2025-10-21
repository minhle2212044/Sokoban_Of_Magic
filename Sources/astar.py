"""
A* (A Star) implementation for Sokoban - based on run_astar.py logic
"""
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
    applyActionSequence,
)


def heuristic(posPlayer, posBox):
    """A heuristic function to calculate the overall distance between boxes and goals"""
    distance = 0
    completes = set(H.posGoals) & set(posBox)
    sortposBox = list(set(posBox).difference(completes))
    sortposGoals = list(set(H.posGoals).difference(completes))
    
    # Handle case where there are different numbers of boxes and goals
    min_length = min(len(sortposBox), len(sortposGoals))
    for i in range(min_length):
        distance += (abs(sortposBox[i][0] - sortposGoals[i][0])) + (abs(sortposBox[i][1] - sortposGoals[i][1]))
    
    # Add penalty for unmatched boxes or goals
    if len(sortposBox) > len(sortposGoals):
        # Extra boxes - add large penalty
        distance += 1000 * (len(sortposBox) - len(sortposGoals))
    elif len(sortposGoals) > len(sortposBox):
        # Extra goals - add large penalty  
        distance += 1000 * (len(sortposGoals) - len(sortposBox))
    
    return distance


def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])


def aStarSearch():
    """A* search implementation - exact logic from run_astar.py"""
    beginBox = PosOfBoxes(H.gameState)
    beginPlayer = PosOfPlayer(H.gameState)

    start_state = (beginPlayer, beginBox)
    frontier = PriorityQueue()
    frontier.push([start_state], heuristic(beginPlayer, beginBox))
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], heuristic(beginPlayer, start_state[1]))
    count = 0
    while frontier:
        if frontier.isEmpty():
            return 'x'
        node = frontier.pop()
        node_action = actions.pop()
        if isEndState(node[-1][-1]):
            solution = ','.join(node_action[1:]).replace(',','')
            print(solution)
            print(count)
            return solution
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            Cost = cost(node_action[1:])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                count = count + 1
                Heuristic = heuristic(newPosPlayer, newPosBox)
                frontier.push(node + [(newPosPlayer, newPosBox)], Heuristic + Cost)
                actions.push(node_action + [action[-1]], Heuristic + Cost)


def astar_search(layout, time_limit=1800):
    """
    A* search wrapper function for main.py integration
    """
    time_start = time.time()
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    
    # Check timeout during search
    solution = aStarSearch()
    
    time_end = time.time()
    if time_end - time_start > time_limit:
        print("Timeout!")
        return 'x'
    
    return solution


def test_astar():
    """Test function"""
    with open("input/1.txt", "r", encoding="utf-8") as f:
        layout = [line.rstrip("\n") for line in f if line.strip() != ""]
    
    solution = astar_search(layout)
    print(f"Final A* solution: {solution}")


if __name__ == "__main__":
    test_astar()
