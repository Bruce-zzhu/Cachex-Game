"""
Functions that help the agent to make decisions
"""

import copy
import random

from pygame2.board import RED, BLUE
from collections import defaultdict


def make_action(board, player):
    """ make decision for next move """

    

    return minimax(board, player, 1)




def greedy_eval(board, player):
    """ calculate critical tokens that contribute to the goal, in the range of 0-5 """
    if player.colour == RED:
        red_critical = count_critical_tokens(board, RED)
        return red_critical
    else:
        blue_critical = count_critical_tokens(board, BLUE)
        return blue_critical

def greedy_proceed(board, player):
    """ directly place to location where contributes the winning """
    actions = {}
    trial = copy.deepcopy(board)
    tried = list(trial.occupied)
    while len(tried) != board.size:
        coord = random_move(trial.occupied, 0, board.n - 1)
        tried.append(coord)
        trial.occupied[coord] = player.colour
        # evaluate the state
        value = greedy_eval(trial, player)
        actions[coord] = value
        # recover the board state
        trial.occupied.pop(coord)
    action = max(actions, key=actions.get)
    #print("Greedy actions ", actions)
    return action




def cutoff_test(board, depth):

    if len(board.occupied) == board.n:
        return True
    # depth
    if len(board.occupied) % depth == 0:
        return True
    
    return False


def eval(board, player):
    """ evaluate the current board state """

    red_critical = blue_critical = 0

    # critical tokens that contribute to the goal, in the range of 0-5
    red_critical = count_critical_tokens(board, RED)
    blue_critical = count_critical_tokens(board, BLUE)

    # number of tokens from one player
    red_tokens = board.count_player_tokens(RED)
    blue_tokens = board.count_player_tokens(BLUE)
    
    red_value = red_critical + (red_tokens - blue_tokens)
    blue_value = blue_critical + (blue_tokens - red_tokens)
    

    if player.colour == RED:
        return red_value 
    else:
        return blue_value



def count_critical_tokens(board, player):
    """ find the tokens that contribute to the goal """
    groups = find_all_groups(board, player)
    critical_length = 0
    for group in groups:
        critical = []
        for token in group:
            if player == RED:
                # find distinguish rows
                if token[0] not in critical:
                    critical.append(token[0])
            elif player == BLUE:
                # find distinguish columns
                if token[1] not in critical:
                    critical.append(token[1])
        cur_length = len(critical)
        if cur_length > critical_length:
            critical_length = cur_length
    
    num_crit_group = 0
    if critical_length > 1:
        for g in groups:
            if len(g) == critical_length:
                num_crit_group += 1

    return critical_length + num_crit_group

def find_all_groups(board, player):
    groups = []
    explored = []
    for c, p in board.occupied.items():
        if p == player and c not in explored:
            group = []
            find_group_tokens(board, c, player, group, explored)
            groups.append(group)
    
    return groups


def find_group_tokens(board, start, player, group, explored):
    group.append(start)
    explored.append(start)
    
    nbs = board.find_neighbours(start, player)
    for nb in nbs:
        if (nb not in explored) and (nb not in group):
            find_group_tokens(board, nb, player, group, explored)


def go_capture(board, player):
    """ try to capture opponent """  
    oppo = player.oppo
    # search for opponent's tokens
    oppo_tokens = board.find_same_tokens(oppo)
    choices = defaultdict(int)
    for t in oppo_tokens:
        # for each opponent, check if it has adjacent opponents
        same_nbs = board.find_neighbours(t, oppo)
        if not same_nbs:
            # cannot perform capture
            continue
        # find empty adjacent places
        emp_nbs = board.find_empty_neighbours(t)
        for nb in emp_nbs:
            trail = copy.deepcopy(board)
            trail.occupied[nb] = player.colour
            if trail.valid_capture(player.colour, nb[0], nb[1]):
                return nb
            res_emp_nbs = emp_nbs
            res_emp_nbs.remove(nb)
            for i in res_emp_nbs:
                captures = trail.valid_capture(player.colour, i[0], i[1])
                if captures:
                    choices[nb] += 1
    if choices:
        action = max(choices, key=choices.get)
        return action
    else:
        return None


def minimax(board, player, depth):
    actions = {}
    alpha = float('-inf')
    beta = float('inf')

    # try each location that is empty
    tried = list(board.occupied)
    while len(tried) != board.size:
        r, q = random_move(tried, 0, board.n - 1)
        tried.append((r, q))
        
        # start of each branching sub-state is the same as the board state
        temp_board = copy.deepcopy(board)
        if not temp_board.is_occupied(r, q):    
            # update current sub-state   
            temp_board.occupied[(r, q)] = player.colour
            captures = temp_board.valid_capture(player.colour, r, q)
            if captures:
                temp_board.capture_update(captures)

            value = get_min_value(temp_board, player, alpha, beta, depth)
            actions[(r, q)] = value
    
    # if next move will reach the end of the game, make corresponding move
    result = check_game_point(board, player)
    if result:
        actions[result[0]] = result[1]

    coord = max(actions, key=actions.get)
    return coord




def get_max_value(board, player, a, b, depth):

    if cutoff_test(board, depth):
        return eval(board, player)

    tried = list(board.occupied)
    while len(tried) != board.size:
        r, q = random_move(tried, 0, board.n - 1)
        tried.append((r, q))
            
        temp_board = copy.deepcopy(board)
        if not temp_board.is_occupied(r, q):
            temp_board.occupied[(r, q)] = player.colour
            captures = temp_board.valid_capture(player.colour, r, q)
            if captures:
                temp_board.capture_update(captures)

            a = max(a, get_min_value(temp_board, player, a, b, depth))
            
            if a >= b:
                return b
    
    return a

def get_min_value(board, player, a, b, depth):

    if cutoff_test(board, depth):
        return eval(board, player)

    tried = list(board.occupied)
    while len(tried) != board.size:
        r, q = random_move(tried, 0, board.n - 1)
        tried.append((r, q))
            
        temp_board = copy.deepcopy(board)
        if not temp_board.is_occupied(r, q):
            temp_board.occupied[(r, q)] = player.oppo
            captures = temp_board.valid_capture(player.oppo, r, q)
            if captures:
                temp_board.capture_update(captures)
            
            b = min(b, get_max_value(temp_board, player, a, b, depth))
            if b <= a:
                return a
    return b


def check_game_point(board, player):
    """ check if next move will end the game """
    for r in range(board.n):
        for q in range(board.n):
            if not board.is_occupied(r, q):
                trial = copy.deepcopy(board)
                # check if I will win the game
                trial.occupied[(r, q)] = player.colour
                winner = trial.end_game()
                if winner == player.colour:
                    return (r, q), float('inf')

                # check if opponent will win the game
                trial.occupied[(r, q)] = player.oppo
                winner = trial.end_game()
                if winner == player.oppo:
                    # attempt to save our life
                    coord, value = attempt_save_life(trial, player, (r, q))
                    if coord:
                        return coord, value
                    # can't save :(
                    return 0
    return 0

def attempt_save_life(end_board, player, game_point):
    # recover the board
    end_board.occupied.pop(game_point)
    # attemp by using capture
    for r in range(end_board.n):
        for q in range(end_board.n):
            if not end_board.is_occupied(r, q):
                trial = copy.deepcopy(end_board)                
                captures = trial.valid_capture(player.colour, r, q)
                if captures:
                    trial.capture_update(captures)
                # put the game point back and check again
                trial.occupied[game_point] = player.oppo
                if not trial.end_game():
                    return (r, q), float('inf')

    # attemp by placing on the game point
    end_board.occupied[game_point] = player.colour
    if not end_board.end_game():
        return game_point, float('inf')
    
    return None, None



# def random_move(board):
#     r = int(random.randint(0, board.n - 1))
#     q = int(random.randint(0, board.n - 1))
#     return r, q

def random_move(occupied, low, high):
    r = int(random.randint(low, high))
    q = int(random.randint(low, high))
    while (r, q) in occupied:
        r = int(random.randint(low, high))
        q = int(random.randint(low, high))
    return r, q