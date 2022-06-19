from referee.game import _ACTION_STEAL, _ACTION_PLACE
from pygame2.board import Board, RED, BLUE
from pygame2.strategy import make_action, random_move


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

        if self.board.is_first_move(self.colour):
            if self.colour == RED:
                r, q = random_move(self.board.occupied, 0, self.board.n - 1)
                # prevent placing on the board center
                if (r, q) == self.board.board_center():
                    r, q = random_move(self.board.occupied, 0, self.board.n - 1)
                return (_ACTION_PLACE, r, q)
            else:
                return (_ACTION_STEAL,)               

        act_r, act_q = make_action(self.board, self)
        
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
        if action[0] == _ACTION_STEAL:
            self.board.steal_update()
        elif action[0] == _ACTION_PLACE:
            r, q = action[1], action[2]
            self.board.place_update(player, r, q)
            captures = self.board.valid_capture(player, r, q)          
            if captures:
                self.board.capture_update(captures)
        
