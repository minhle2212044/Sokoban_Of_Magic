import time
import sokoban_helpers as H
from sokoban_helpers import (
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


def dfsSearch():
    beginBox = PosOfBoxes(H.gameState)
    beginPlayer = PosOfPlayer(H.gameState)
    
    # Check if already solved
    if isEndState(beginBox):
        print("Already solved!")
        return "", 0
    
    # DFS uses a stack instead of priority queue
    stack = [(beginPlayer, beginBox, "")]  # (player_pos, box_pos, actions)
    exploredSet = set()
    count = 0
    
    startStateKey = (beginPlayer, beginBox)
    exploredSet.add(startStateKey)
    count += 1
    
    while stack:
        posPlayer, posBox, actions = stack.pop()
        
        # Check if we found the solution
        if isEndState(posBox):
            solution = actions
            print(f"Solution found: {solution}")
            print(f"States explored: {count}")
            return solution, count
        
        # Generate all possible moves from current state
        for action in legalActions(posPlayer, posBox):
            newPosPlayer, newPosBox = updateState(posPlayer, posBox, action)
            
            newStateKey = (newPosPlayer, newPosBox)
            
            if isFailed(newPosBox): 
                continue
                
            if newStateKey in exploredSet:
                continue
            
            exploredSet.add(newStateKey)
            count += 1
            
            newActions = actions + action[-1]
            stack.append((newPosPlayer, newPosBox, newActions))   
    
    print("No solution found")
    return 'x', count


def dfs_search(layout, time_limit=1200):
    """
    DFS search wrapper function for main.py integration
    """
    time_start = time.time()
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    
    solution, explored_count = dfsSearch()
    
    time_end = time.time()
    if time_end - time_start > time_limit:
        print("Timeout!")
        return 'x', explored_count
    
    return solution, explored_count


def test_dfs():
    """Test function"""
    with open("input/1.txt", "r", encoding="utf-8") as f:
        layout = [line.rstrip("\n") for line in f if line.strip() != ""]
    
    solution, count = dfs_search(layout)
    print(f"Final DFS solution: {solution}, Explored: {count}")


if __name__ == "__main__":
    test_dfs()