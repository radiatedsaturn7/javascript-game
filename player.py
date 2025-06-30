import math

class Player:
    """Represents the player's position, orientation and state."""

    BASE_ACCEL = 0.02
    BOOST_ACCEL = 0.05
    BOOST_DURATION = 20  # frames

    def __init__(self, x: float = 1.0, y: float = 1.0, health: int = 100):
        self.x = x
        self.y = y
        self.angle = 0.0  # 0 radians faces upward
        self.speed = 0.0
        self.throttle = False
        self.health = health
        self._boost_frames = 0

    def turn_left(self):
        self.angle -= 0.1

    def turn_right(self):
        self.angle += 0.1

    def update(self):
        accel = self.BOOST_ACCEL if self._boost_frames > 0 else self.BASE_ACCEL
        max_speed = 1.5 if self._boost_frames > 0 else 1.0

        if self.throttle:
            self.speed = min(self.speed + accel, max_speed)
        else:
            self.speed = max(self.speed - self.BASE_ACCEL, 0.0)

        if self._boost_frames > 0:
            self._boost_frames -= 1

        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def start_boost(self):
        if self._boost_frames > 0:
            return
        cost = 19
        available = self.health - 1
        if available <= 0:
            return
        if available < cost:
            ratio = available / cost
            self._boost_frames = max(1, int(self.BOOST_DURATION * ratio))
            self.health = 1
        else:
            self._boost_frames = self.BOOST_DURATION
            self.health -= cost
