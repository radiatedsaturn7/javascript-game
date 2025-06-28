class Player:
    """Represents the player's racer."""

    def __init__(self, lanes=5):
        self.lanes = lanes
        self.position = lanes // 2  # start in the middle lane

    def move_left(self):
        if self.position > 0:
            self.position -= 1

    def move_right(self):
        if self.position < self.lanes - 1:
            self.position += 1
