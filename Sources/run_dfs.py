import argparse
import os
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
    DFS search implementation using the same structure as A* but with DFS logic.
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


def solve_dfs(layout):
    """
    Solve the Sokoban puzzle using DFS algorithm.
    Similar structure to solve_astar but uses DFS logic.
    """
    time_start = time.time()
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    solution = dfsSearch()
    time_end = time.time()
    time_str = '%.2f seconds.' % (time_end - time_start)
    print(solution)
    print('Runtime of %s: %.2f second.' % ('dfs', time_end - time_start))
    return solution, time_str


def read_layout_from_file(path):
    """Read layout from file, same as in run_astar.py"""
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip() != ""]


def write_output(path, solution, runtime, layout):
    """Write output to file, same as in run_astar.py"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"solution={solution}\n")
        f.write(f"runtime={runtime}\n")
        if solution and solution != 'x':
            snapshots = applyActionSequence(layout, solution)
            for title, board, sep in snapshots:
                f.write("\n" + title + "\n")
                f.write(board + "\n")
                f.write(sep + "\n")


def main():
    """Main function with command line interface, same structure as run_astar.py"""
    parser = argparse.ArgumentParser(description="Run Sokoban DFS solver with custom input and write result to file.")
    parser.add_argument("--input", dest="input_path", help="Path to input map file (e.g. input/1.txt)")
    parser.add_argument("--output", dest="output_path", help="Path to write output (e.g. output.txt)")
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    if not input_path:
        input_path = input("Nhap duong dan file input (vi du: input/2.txt): ").strip()
    if not output_path:
        output_path = input("Nhap duong dan file output (vi du: result.txt): ").strip()

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Khong tim thay file input: {input_path}")

    layout = read_layout_from_file(input_path)

    solution, runtime = solve_dfs(layout)

    write_output(output_path, solution, runtime, layout)
    print(f"Da ghi ket qua vao: {output_path}")


if __name__ == "__main__":
    main()
