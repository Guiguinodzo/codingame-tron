class Grid:
    width: int
    height: int
    data: list[list[int]]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [([-1] * height) for _ in range(width)]

    def set(self, x, y, value):
        self.data[x][y] = value

    def get(self, x, y):
        return self.data[x][y]

    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def replace(self, old_value, new_value):
        for x in range(self.width):
            for y in range(self.height):
                if self.data[x][y] == old_value:
                    self.data[x][y] = new_value
