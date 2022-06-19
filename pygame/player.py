import time
from referee.game import _ACTION_STEAL, _ACTION_PLACE
from pygame.board import Board, RED, BLUE
from pygame.strategy import make_action, random_first_move

class Player:
    def __init__(self, player, n):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string red if your player will
        play as Red, or the string blue if your player will play
        as Blue.
        """
        self.colour = player
        self.board = Board(n)
        self.total_time = 0          # Keep track of time
        self.turn_time = 0
        self.oppo = None
        if player == RED:
            self.oppo = BLUE
        else:
            self.oppo = RED

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        self.turn_time = time.time()
        if self.board.is_first_move(self.colour):
            if self.colour == RED:
                r, q = random_first_move(self.board, 0, self.board.n - 1)
                return (_ACTION_PLACE, r, q)
            else:
                return (_ACTION_STEAL,)         
        act_r, act_q = make_action(self.board, self)

        # Prevent draws from happening (by keeping track of game configurations (in turn function))
        old = [(act_r, act_q)]
        self.board.occupied[old[0]] = self.colour
        captures = None
        captures = self.board.valid_capture(self.colour, act_r, act_q)          
        if captures:
            self.board.capture_update(captures)

        # Find another move if about to make a move that makes a configuration thats happened 6 times before
        while self.board.same_count.get(frozenset(self.board.occupied.items())) == 6:
            self.board.recover_board(self.colour, None, captures)

            for i in old:
                self.board.occupied[i] = self.colour
            
            act_r, act_q = make_action(self.board, self)

            for i in old:
                self.board.occupied.pop(i)

            self.board.occupied[(act_r, act_q)] = self.colour
            captures = self.board.valid_capture(self.colour, act_r, act_q)          
            if captures:
                self.board.capture_update(captures)
            old.append((act_r, act_q))

        self.board.recover_board(self.colour, (act_r, act_q), captures)
        return (_ACTION_PLACE, act_r, act_q)
        
    def turn(self, player, action):
        """
        Called at the end of each player's turn to inform this player of 
        their chosen action. Update your internal representation of the 
        game state based on this. The parameter action is the chosen 
        action itself. 
        
        Note: At the end of your player's turn, the action parameter is
        the same as what your player returned from the action method
        above. However, the referee has validated it at this point.
        """
        if player == self.colour:
            self.total_time = self.total_time + (time.time() - self.turn_time )

        if action[0] == _ACTION_STEAL:
            self.board.steal_update()
        elif action[0] == _ACTION_PLACE:
            r, q = action[1], action[2]
            self.board.place_update(player, r, q)
            captures = self.board.valid_capture(player, r, q)          
            if captures:
                self.board.capture_update(captures)

        # Keeping track of game configurations
        if frozenset(self.board.occupied.items()) in self.board.same_count:
            self.board.same_count[frozenset(self.board.occupied.items())] = self.board.same_count[frozenset(self.board.occupied.items())] + 1
        else:
            self.board.same_count[frozenset(self.board.occupied.items())] = 1