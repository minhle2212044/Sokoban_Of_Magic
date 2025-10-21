import argparse
import os
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
    return len([x for x in actions if x.islower()])


def aStarSearch():
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


def solve_astar(layout):
    time_start = time.time()
    H.gameState = transferToGameState(layout)
    H.posWalls = PosOfWalls(H.gameState)
    H.posGoals = PosOfGoals(H.gameState)
    solution = aStarSearch()
    time_end=time.time()
    time_str = '%.2f seconds.' %(time_end-time_start)
    print(solution)
    print('Runtime of %s: %.2f second.' %('astar', time_end-time_start))
    return solution, time_str


def read_layout_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip() != ""]


def write_output(path, solution, runtime, layout):
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
    parser = argparse.ArgumentParser(description="Run Sokoban A* solver with custom input and write result to file.")
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

    solution, runtime = solve_astar(layout)

    write_output(output_path, solution, runtime, layout)
    print(f"Da ghi ket qua vao: {output_path}")


if __name__ == "__main__":
    main()


