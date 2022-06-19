"""
Functions that help the agent make decisions
"""

import random
from pygame.board import RED, BLUE
from collections import defaultdict

def make_action(board, player):
    """
    Make decision for next move.
    """
    
    # Use greedy method when the time is close to the maximum 
    if player.total_time > (board.n ** 2 - 5):
        return greedy_proceed(board, player)

    # Evaluate the current state
    value = eval(board, player.colour)
    oppo_value = eval(board, player.oppo)

    if board.n > 13:
        # Use greedy method to save time at the start
        if len(board.occupied) < board.n:
            return greedy_proceed(board, player)

        # When we have an advantage reduce cutoff depth for minimax 
        if value > oppo_value:
            return minimax(board, player, 1)

    # Low utility, aim for defense by capturing
    if value < oppo_value:
        result = check_game_point(board, player)

        if result:
            return result[0]
        action = go_capture(board, player)
        
        if action:
            return action
    
    # Minimax cutoff depth depending on the board size and time constraint
    if board.n <= 5:
        return minimax(board, player, 3)
    else:
        
        return minimax(board, player, 2)

def greedy_eval(board, player):
    """
    Calculate critical tokens that contribute to the goal, in the range of 0-n.
    """
    if player == RED:
        red_critical = count_criticals(board, RED)
        return red_critical
    else:
        blue_critical = count_criticals(board, BLUE)
        return blue_critical

def greedy_proceed(board, player):
    """
    Directly place to location where contributes to the winning.
    """
    actions = {}
    tried = list(board.occupied)

    while len(tried) != board.size:
        coord = random_move(board.occupied, 0, board.n - 1)
        if coord in tried:
            continue
        tried.append(coord)
        board.occupied[coord] = player.colour

        # Evaluate the state
        value = greedy_eval(board, player)
        actions[coord] = value

        # Recover the board state
        board.occupied.pop(coord)

    action = max(actions, key=actions.get)
    return action

def cutoff_test(board, depth):
    """
    Set a depth for minimax exploration.
    """
    if len(board.occupied) == board.size:
        return True
    # Depth
    if len(board.occupied) % depth == 0:
        return True
    return False

def eval(board, player):
    """
    Evaluate the current board state.
    """
    red_critical = blue_critical = 0

    # Critical tokens that contribute to the goal, in the range of 0-n
    red_critical = count_criticals(board, RED)
    blue_critical = count_criticals(board, BLUE)

    # Number of tokens from one player
    red_tokens = board.count_player_tokens(RED)
    blue_tokens = board.count_player_tokens(BLUE)
    
    red_value = red_critical + (red_tokens - blue_tokens)
    blue_value = blue_critical + (blue_tokens - red_tokens)
    
    if player == RED:
        return red_value 
    else:
        return blue_value

def count_criticals(board, player):
    """
    Find the number of tokens/token groups that contribute to the goal.
    """
    # A token group is a bunch of tokens that are adjacent to each other.
    groups = find_all_groups(board, player)
    
    # The number of distinguishable rows/columns the player has occupied, in the range of 0-n
    critical_length = 0
    group_crit = {}
    for group in groups:
        critical = []
        for token in group:
            # Find distinguishable rows and columns
            if player == RED:
                if token[0] not in critical:
                    critical.append(token[0])
            elif player == BLUE:
                if token[1] not in critical:
                    critical.append(token[1])

        cur_length = len(critical)
        group_crit[groups.index(group)] = cur_length
        if cur_length > critical_length:
            critical_length = cur_length
    
    # The number of groups that could be impactful
    num_crit_group = 0

    # Count groups that have all critical tokens
    # Does not matter to the game (generally) if the length <= 2
    if critical_length > 2:
        for v in group_crit.values():
            if v == critical_length:
                num_crit_group += 1

    return critical_length + num_crit_group

def find_all_groups(board, player):
    """
    Find all token groups.
    A token group is a bunch of tokens that are adjacent to each other.
    """
    groups = []
    explored = []
    for c, p in board.occupied.items():
        if p == player and c not in explored:
            group = []
            find_group_tokens(board, c, player, group, explored)
            groups.append(group)
    return groups

def find_group_tokens(board, start, player, group, explored):
    """
    Find each adjacent tokens starting from one token.
    """
    group.append(start)
    explored.append(start)
    
    nbs = board.find_neighbours(start, player)
    for nb in nbs:
        if (nb not in explored) and (nb not in group):
            find_group_tokens(board, nb, player, group, explored)

def go_capture(board, player):
    """
    Try to capture opponent.
    """  
    oppo = player.oppo

    # Search for opponent's tokens
    oppo_tokens = board.find_same_tokens(oppo)
    choices = defaultdict(int)

    for t in oppo_tokens:
        # For each opponent, find empty adjacent hexes
        emp_nbs = board.find_empty_neighbours(t)
        for nb in emp_nbs:
            # Try if it can perform capture directly
            board.occupied[nb] = player.colour
            if board.valid_capture(player.colour, nb[0], nb[1]):
                board.occupied.pop(nb)
                return nb

            # If the trial above fails and if this is not a dangerous place, 
            # think about doing it in next move
            if not board.capture_danger(player.oppo, nb[0], nb[1]):
                res_emp_nbs = emp_nbs
                # Make sure not to consider nb
                res_emp_nbs.remove(nb)
                for i in res_emp_nbs:
                    captures = board.valid_capture(player.colour, i[0], i[1])
                    if captures:
                        choices[nb] += 1
            board.occupied.pop(nb)

    # Choose the move that captures the most opponents
    if choices:
        action = max(choices, key=choices.get)
        return action
    else:
        return None

def minimax(board, player, depth):
    actions = {}
    alpha = float('-inf')
    beta = float('inf')

    # Try each location that is empty
    tried = list(board.occupied)
    while len(tried) != board.size:
        r, q = random_move(tried, 0, board.n - 1)
        tried.append((r, q))
        
        # Start of each branching sub-state is the same as the board state
        if not board.is_occupied(r, q):    
            # Update current sub-state   
            board.occupied[(r, q)] = player.colour
            captures = board.valid_capture(player.colour, r, q)
            if captures:
                board.capture_update(captures)

            value = get_min_value(board, player, alpha, beta, depth)
            actions[(r, q)] = value

            # Return to original state
            board.recover_board(player.colour, (r, q), captures)
        
    # If next move will reach the end of the game, make corresponding move
    result = check_game_point(board, player)
    if result:
        actions[result[0]] = result[1]

    coord = max(actions, key=actions.get)
    return coord

def get_max_value(board, player, a, b, depth):
    if cutoff_test(board, depth):
        return eval(board, player.colour)

    tried = list(board.occupied)
    while len(tried) != board.size:
        r, q = random_move(tried, 0, board.n - 1)
        tried.append((r, q))
            
        if not board.is_occupied(r, q):
            board.occupied[(r, q)] = player.colour
            captures = board.valid_capture(player.colour, r, q)
            if captures:
                board.capture_update(captures)

            a = max(a, get_min_value(board, player, a, b, depth))
            
            # Return to original state
            board.recover_board(player.colour, (r, q), captures)

            if a >= b:
                return b
    return a

def get_min_value(board, player, a, b, depth):
    if cutoff_test(board, depth):
        return eval(board, player.colour)

    tried = list(board.occupied)
    while len(tried) != board.size:
        r, q = random_move(tried, 0, board.n - 1)
        tried.append((r, q))
            
        if not board.is_occupied(r, q):
            board.occupied[(r, q)] = player.oppo
            captures = board.valid_capture(player.oppo, r, q)
            if captures:
                board.capture_update(captures)
            
            b = min(b, get_max_value(board, player, a, b, depth))
            
            # Return to original state
            board.recover_board(player.oppo, (r, q), captures)
            
            if b <= a:
                return a
    return b

def check_game_point(board, player):
    """
    Check if next move ends the game.
    """
    for r in range(board.n):
        for q in range(board.n):
            if not board.is_occupied(r, q):                
                # Check if we win the game
                board.occupied[(r, q)] = player.colour
                winner = board.end_game()
                if winner == player.colour:
                    board.occupied.pop((r, q))
                    return (r, q), float('inf')

                # If opponent wins the game, attempt to save our life
                board.occupied[(r, q)] = player.oppo
                winner = board.end_game()
                if winner == player.oppo:
                    coord, value = attempt_save_life(board, player, (r, q))
                    board.occupied.pop((r, q))
                    if coord:
                        return coord, value
                    return 0

                board.occupied.pop((r, q))
    return 0

def attempt_save_life(board, player, game_point):
    # Return to original state
    board.occupied.pop(game_point)

    # Attemp by using capture
    for r in range(board.n):
        for q in range(board.n):
            if not board.is_occupied(r, q) and game_point != (r, q):           
                board.occupied[(r, q)] = player.colour
                captures = board.valid_capture(player.colour, r, q)
                if captures:
                    board.capture_update(captures)
                    # Put the game point back and check again
                    board.occupied[game_point] = player.oppo
                    if not board.end_game():
                        board.recover_board(player.colour, (r, q), captures)
                        return (r, q), float('inf')

                board.recover_board(player.colour, (r, q), captures)

    # Attemp by placing on the game point
    board.occupied[game_point] = player.colour
    if not board.end_game():
        return game_point, float('inf')
    return None, None

def random_move(occupied, low, high):
    r = int(random.randint(low, high))
    q = int(random.randint(low, high))
    while (r, q) in occupied:
        r = int(random.randint(low, high))
        q = int(random.randint(low, high))
    return r, q

def random_first_move(board, low, high):
    r = int(random.randint(low, high))
    q = int(random.randint(low, high))
    if board.is_first_move(RED) and (r, q) == board.board_center():
        while (r, q) == board.board_center():
            r = int(random.randint(low, high))
            q = int(random.randint(low, high))
    return r, q