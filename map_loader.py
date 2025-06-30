class Map:
    """Represents a simple ASCII race track loaded from lines of text."""

    def __init__(self, lines):
        self.lines = [line.rstrip('\n') for line in lines]
        self.height = len(self.lines)
        self.width = max(len(line) for line in self.lines) if self.lines else 0

        self.start_x = 1
        self.start_y = self.height - 2
        for y, line in enumerate(self.lines):
            x = line.find('S')
            if x != -1:
                self.start_x = x
                self.start_y = y
                # remove the start marker so it is treated as driveable
                self.lines[y] = line.replace('S', ' ', 1)
                break

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            return cls([line.rstrip('\n') for line in f])

    def char_at(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= iy < self.height and 0 <= ix < len(self.lines[iy]):
            return self.lines[iy][ix]
        return 'o'  # treat out-of-bounds as wall
