"""
Board representation
"""

from referee.game import COLOURS
import copy
from collections import defaultdict

RED = COLOURS[0]
BLUE = COLOURS[1]

class Board:

    n: int
    occupied: dict

    def __init__(self, n):
        self.n = n
        self.occupied = {}  # store tokens on the board
        self.size = n ** 2


    def inbounds(self, coord):
        r, q = coord
        return r >= 0 and r < self.n and q >= 0 and q < self.n


    def steal_update(self):
        """ update the board state when a STEAL action happened """
        r, q = list(self.occupied)[0]
        self.occupied.pop((r, q))
        self.occupied[(q, r)] = BLUE


    
    def place_update(self, player, r, q):
        """ update the board state when a PLACE action happened """
        self.occupied[(r, q)] = player


    def remove(self, r, q):
        """ remove a token from the board """
        self.occupied.pop((r, q))
        


    def capture_update(self, captures):
        """ remove multiple tokens if a CAPTURE action happened """
        for i in captures:
            self.remove(i[0], i[1])


    def valid_capture(self, player, r, q):
        """ check if a CAPTURE action can happen """
        captures = set()
        # top
        if self.valid_capture_diamond(player, (r+2, q-1), (r+1, q-1), (r+1, q)):
            captures.add((r+1, q-1))
            captures.add((r+1, q))
        # top right close
        if self.valid_capture_diamond(player, (r+1, q), (r+1, q-1), (r, q+1)):
            captures.add((r+1, q-1))
            captures.add((r, q+1))
        # top right far
        if self.valid_capture_diamond(player, (r+1, q+1), (r+1, q), (r, q+1)):
            captures.add((r+1, q))
            captures.add((r, q+1))
        # right
        if self.valid_capture_diamond(player, (r, q+1), (r+1, q), (r-1, q+1)):
            captures.add((r+1, q))
            captures.add((r-1, q+1))
        # bottom right far
        if self.valid_capture_diamond(player, (r-1, q+2), (r, q+1), (r-1, q+1)):
            captures.add((r, q+1))
            captures.add((r-1, q+1))
        # bottom right close
        if self.valid_capture_diamond(player, (r-1, q+1), (r-1, q), (r, q+1)):
            captures.add((r-1, q))
            captures.add((r, q+1))
        # bottom
        if self.valid_capture_diamond(player, (r-2, q+1), (r-1, q), (r-1, q+1)):
            captures.add((r-1, q))
            captures.add((r-1, q+1))
        # bottom left far
        if self.valid_capture_diamond(player, (r-1, q-1), (r, q-1), (r-1, q)):
            captures.add((r, q-1))
            captures.add((r-1, q))
        # bottom left close
        if self.valid_capture_diamond(player, (r-1, q), (r, q-1), (r-1, q+1)):
            captures.add((r, q-1))
            captures.add((r-1, q+1))
        # left
        if self.valid_capture_diamond(player, (r, q-1), (r-1, q), (r+1, q-1)):
            captures.add((r-1, q))
            captures.add((r+1, q-1))
        # top left far
        if self.valid_capture_diamond(player, (r+1, q-2), (r, q-1), (r+1, q-1)):
            captures.add((r, q-1))
            captures.add((r+1, q-1))
        # top left close
        if self.valid_capture_diamond(player, (r+1, q-1), (r, q-1), (r+1, q)):
            captures.add((r, q-1))
            captures.add((r+1, q))

        return captures



    def valid_capture_diamond(self, player, diag, left, right):
        """ check if a valid capture diamond is formed """
        if (not self.inbounds(diag)) or (not self.inbounds(left)) or (not self.inbounds(right)):
            return False

        if (diag in self.occupied) and (left in self.occupied) and (right in self.occupied):
            if self.occupied[diag] == player and self.occupied[left] != player and \
                                                self.occupied[right] != player:
                return True
        return False


    def is_occupied(self, r, q):        
        return (r, q) in self.occupied   



    def end_game(self):        
        """ check if the game ends and return the winner """
        for r, q in self.occupied.keys():
            if r == 0 and self.occupied[(r, q)] == RED:
                if self.dfs_search((r, q), lambda t: t[0] == self.n - 1, RED):
                    return RED
        
        for r, q in self.occupied.keys():
            if q == 0 and self.occupied[(r, q)] == BLUE:
                if self.dfs_search((r, q), lambda t: t[1] == self.n - 1, BLUE):
                    return BLUE
        return None

    def dfs_search(self, start, reach_goal, player):
        explored = []
        nbs = self.find_neighbours(start, player)
        explored.append(start)
        for nb in nbs:
            if nb not in explored:
                end = self.token_crawler(explored, nb, reach_goal, player)
                if end:
                    return True
        return False

    def token_crawler(self, explored, start, reach_goal, player):
        """ DFS implementation, crawl adjacent tokens """
        if reach_goal(start):
            return True
        explored.append(start)
        nbs = self.find_neighbours(start, player)
        for nb in nbs:
            if nb not in explored:
                end = self.token_crawler(explored, nb, reach_goal, player)
                if end:
                    return True
        return False
                
        

    def is_first_move(self, player):
        if player == RED:
            return len(self.occupied) == 0
        else:
            return len(self.occupied) == 1

    
    def find_neighbours(self, coord, player=None):
        """ find all neighbouring same tokens or coordinates """
        (r, q) = coord
        nb_1 = (r + 1, q - 1)       # Top left
        nb_2 = (r,     q - 1)       # Left
        nb_3 = (r - 1, q)           # Bottom left
        nb_4 = (r + 1, q)           # Top right
        nb_5 = (r,     q + 1)       # Right
        nb_6 = (r - 1, q + 1)       # Bottom right
        neighbours = [nb_1, nb_2, nb_3, nb_4, nb_5, nb_6]
        valid_nbs = list(filter(lambda nb: self.inbounds(nb), neighbours))
        if player:
            player_nbs = list(filter(lambda nb: nb in self.occupied and self.occupied[nb] == player, valid_nbs))
            return player_nbs
        else:
            return valid_nbs

    def find_empty_neighbours(self, coord):
        """ find all neighbouring empty coordinates """
        (r, q) = coord
        nb_1 = (r + 1, q - 1)       # Top left
        nb_2 = (r,     q - 1)       # Left
        nb_3 = (r - 1, q)           # Bottom left
        nb_4 = (r + 1, q)           # Top right
        nb_5 = (r,     q + 1)       # Right
        nb_6 = (r - 1, q + 1)       # Bottom right
        neighbours = [nb_1, nb_2, nb_3, nb_4, nb_5, nb_6]
        valid_nbs = list(filter(lambda nb: self.inbounds(nb), neighbours))
        empty_nbs = list(filter(lambda nb: nb not in self.occupied, valid_nbs))
        return empty_nbs

    def capture_danger(self, opponent, r, q):
        """ check if our move may cause a capture to us """
        empty_nbs = self.find_empty_neighbours((r, q))
        for (nr, nq) in empty_nbs:
            if self.valid_capture(opponent, nr, nq):
                return True
        return False
    
    def almost_capture(self, player, r, q):
        """ check if we can perform capture in two moves """
        trial = copy.deepcopy(self)
        trial.occupied[(r, q)] = player
        choices = defaultdict(int)
        # find neighbours that are opponents
        oppo_nbs = self.find_neighbours((r, q), player.oppo)
        if oppo_nbs:
            for op in oppo_nbs:
                emp_nbs = self.find_empty_neighbours(op)
                for nb in emp_nbs:
                    # check if capture can happen by placing a token
                    captures = self.valid_capture(player.colour, nb[0], nb[1])
                    if captures:
                        # increase desirability 
                        choices[nb] += len(captures) 

        if choices:
            # get the coordinate with max desirability
            coord = max(choices, key=choices.get)
            return coord
        else:
            return None



        
    def find_same_tokens(self, player):
        """ find all the same tokens on the board """
        tokens = []
        for c, p in self.occupied.items():
            if p == player:
                tokens.append(c)
        return tokens

    def is_full(self):
        return len(self.occupied) == self.n

    def count_player_tokens(self, player):
        return list(self.occupied.values()).count(player)

    def board_center(self):
        center = 0
        if self.n % 2 != 0:
            center = self.n // 2
        else:
            center = (self.n + 1) // 2
        return (center, center)

