import math
import time

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
        self.lean = 0.0
        self.frame = 0
        self.lap = 1
        self.best_lap = None
        self._lap_start = time.time()
        self.start_time = time.time()

    def direction_arrow(self) -> str:
        """Return an ASCII arrow representing the facing direction."""
        angle = self.angle % (2 * math.pi)
        if angle < math.pi / 4 or angle >= 7 * math.pi / 4:
            return '^'
        elif angle < 3 * math.pi / 4:
            return '>'
        elif angle < 5 * math.pi / 4:
            return 'v'
        else:
            return '<'

    def turn_left(self):
        self.angle -= 0.1
        self.lean = max(self.lean - 0.5, -1.0)

    def turn_right(self):
        self.angle += 0.1
        self.lean = min(self.lean + 0.5, 1.0)

    def update(self):
        accel = self.BOOST_ACCEL if self._boost_frames > 0 else self.BASE_ACCEL
        max_speed = 1.5 if self._boost_frames > 0 else 1.0

        if self.throttle:
            self.speed = min(self.speed + accel, max_speed)
        else:
            self.speed = max(self.speed - self.BASE_ACCEL, 0.0)

        if self._boost_frames > 0:
            self._boost_frames -= 1

        # slowly return lean to neutral
        if self.lean > 0:
            self.lean = max(0, self.lean - 0.1)
        elif self.lean < 0:
            self.lean = min(0, self.lean + 0.1)

        self.frame = (self.frame + 1) % 2

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

    @property
    def boosting(self) -> bool:
        """Return True while boost is active."""
        return self._boost_frames > 0

    def total_time(self) -> float:
        return time.time() - self.start_time

    def complete_lap(self):
        lap_time = time.time() - self._lap_start
        if self.best_lap is None or lap_time < self.best_lap:
            self.best_lap = lap_time
        self.lap += 1
        self._lap_start = time.time()
