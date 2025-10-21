"""
DFS (Depth First Search) implementation for Sokoban - based on run_dfs.py logic
"""
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
    applyActionSequence,
)


def dfsSearch():
    """
    DFS search implementation - exact logic from run_dfs.py
    Returns the solution string or 'x' if no solution found.
    """
    beginBox = PosOfBoxes(H.gameState)
    beginPlayer = PosOfPlayer(H.gameState)
    
    # Check if already solved
    if isEndState(beginBox):
        print("Already solved!")
        return ""
    
    # DFS uses a stack instead of priority queue
    stack = [(beginPlayer, beginBox, "")]  # (player_pos, box_pos, actions)
    exploredSet = set()
    count = 0
    
    while stack:
        posPlayer, posBox, actions = stack.pop()
        
        # Check if this state is already explored
        state_key = (posPlayer, posBox)
        if state_key in exploredSet:
            continue
            
        exploredSet.add(state_key)
        count += 1
        
        # Check if we found the solution
        if isEndState(posBox):
            solution = actions
            print(f"Solution found: {solution}")
            print(f"States explored: {count}")
            return solution
        
        # Generate all possible moves from current state
        for action in legalActions(posPlayer, posBox):
            newPosPlayer, newPosBox = updateState(posPlayer, posBox, action)
            
            # Skip if this state leads to failure
            if isFailed(newPosBox):
                continue
                
            # Add to stack for DFS exploration
            newActions = actions + action[-1]  # action[-1] is the move character
            stack.append((newPosPlayer, newPosBox, newActions))
    
    print("No solution found")
    return 'x'


def dfs_search(layout, time_limit=1800):
    """
    DFS search wrapper function for main.py integration
    """
    time_start = time.time()
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    
    solution = dfsSearch()
    
    time_end = time.time()
    if time_end - time_start > time_limit:
        print("Timeout!")
        return 'x'
    
    return solution


def test_dfs():
    """Test function"""
    with open("input/1.txt", "r", encoding="utf-8") as f:
        layout = [line.rstrip("\n") for line in f if line.strip() != ""]
    
    solution = dfs_search(layout)
    print(f"Final DFS solution: {solution}")


if __name__ == "__main__":
    test_dfs()