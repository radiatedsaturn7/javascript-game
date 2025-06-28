class Map:
    """Represents a simple ASCII race track loaded from lines of text."""

    def __init__(self, lines):
        self.lines = [line.rstrip('\n') for line in lines]
        self.height = len(self.lines)
        self.width = max(len(line) for line in self.lines) if self.lines else 0

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            return cls([line.rstrip('\n') for line in f])

    def char_at(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= iy < self.height and 0 <= ix < len(self.lines[iy]):
            return self.lines[iy][ix]
        return 'o'  # treat out-of-bounds as wall
