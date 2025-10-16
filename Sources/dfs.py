import support_function_for_dfs as spf
import time

def recursive_dfs(current_state, list_state_visited, list_check_point, start_time):
    # Use list_state_visited (list or set) to check for visited/duplicate states
    
    # 1. Check for Timeout
    if time.time() - start_time > spf.TIME_OUT:
        return ([], -1) # Return Timeout signal

    cur_pos = spf.find_position_player(current_state.board)
    list_can_move = spf.get_next_pos(current_state.board, cur_pos)
    
    for next_pos in list_can_move:
        new_board = spf.move(current_state.board, next_pos, cur_pos, list_check_point)
        
        # Avoid duplicate states
        if spf.is_board_exist(new_board, list_state_visited):
            continue
            
        # Check for Deadlock
        if spf.is_board_can_not_win(new_board, list_check_point) or \
           spf.is_all_boxes_stuck(new_board, list_check_point):
            continue

        # Create new state
        new_state = spf.state(new_board, current_state, list_check_point)
        
        # Add the new state to the list of visited states (crucial for recursion)
        list_state_visited.append(new_state)
        
        # 2. Check for Goal
        if spf.check_win(new_board, list_check_point):
            return (new_state.get_line(), len(list_state_visited)) 
        
        # 3. Recursively call the search function on the new state
        result_path, result_count = recursive_dfs(new_state, list_state_visited, list_check_point, start_time)
        
        # Handle recursion results
        if result_count == -1: # Timeout
            return ([], -1)
        if result_path: # Found a path
            return (result_path, result_count)

    return ([], len(list_state_visited)) # No path found from this branch

def DFS_search(board, list_check_point): # Note: Function name should be DFS_search
    start_time = time.time()
    
    start_state = spf.state(board, None, list_check_point)
    list_state_visited = [start_state] 
    
    if spf.check_win(board, list_check_point):
        print("Found win")
        return [board]

    path, count = recursive_dfs(start_state, list_state_visited, list_check_point, start_time)
    
    if count == -1:
        print("Timeout")
        return []
        
    if path:
        print("Found win")
        return (path, count)
    else:
        print("Not Found")
        return []