import random
from collections import deque

class TrackSegment:
    """Represents a portion of the track with constant curvature."""

    def __init__(self, curve: int, length: int):
        self.curve = curve  # -1 left, 1 right, 0 straight
        self.length = length


def segment_generator():
    """Yield endless random track segments."""
    while True:
        curve = random.choice([-1, -1, 0, 0, 0, 1, 1])
        length = random.randint(5, 15)
        yield TrackSegment(curve, length)


class Track:
    def __init__(self):
        self._segments = deque()
        self._gen = segment_generator()
        self._current = next(self._gen)
        self._timer = self._current.length
        self.offset = 0.0

    def update(self) -> float:
        """Advance the track state and return the current horizontal offset."""
        if self._timer <= 0:
            self._current = next(self._gen)
            self._timer = self._current.length
        self.offset += self._current.curve * 0.02
        self._timer -= 1
        # Clamp offset to reasonable range
        self.offset = max(min(self.offset, 1.0), -1.0)
        return self.offset
