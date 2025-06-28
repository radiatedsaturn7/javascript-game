import math

class Player:
    """Represents the player's position and orientation on the map."""

    def __init__(self, x=1.0, y=1.0):
        self.x = x
        self.y = y
        self.angle = 0.0  # 0 radians faces upward
        self.speed = 0.0
        self.throttle = False

    def turn_left(self):
        self.angle -= 0.1

    def turn_right(self):
        self.angle += 0.1

    def update(self):
        if self.throttle:
            self.speed = min(self.speed + 0.02, 1.0)
        else:
            self.speed = max(self.speed - 0.02, 0.0)
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
