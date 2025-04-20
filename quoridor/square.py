class Square:
    def __init__(self):
        # Path availability: True if movement is allowed in that direction
        self.can_move_up = True
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True
        # Indicates if a player is currently on this square
        self.has_player = False

    def __repr__(self):
        return (f"Square(U:{self.can_move_up}, D:{self.can_move_down}, "
                f"L:{self.can_move_left}, R:{self.can_move_right}, "
                f"P:{self.has_player})")
