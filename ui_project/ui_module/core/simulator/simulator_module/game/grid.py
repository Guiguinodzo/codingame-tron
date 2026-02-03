import copy

from ui_module.core.simulator.simulator_module.util.logger import Logger

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

    def print(self, logger: Logger):
        header = "_| " + " ".join([str(i % 10) for i in range(self.width)])
        logger.log(header)
        for y in range(self.height):
            line = f"{y % 10}|"
            for x in range(self.width):
                value = self.get(x, y)
                line += " " + (str(value) if value >= 0 else '.')
            logger.log(line)


    def __deepcopy__(self, _):
        new_grid = Grid(self.width, self.height)
        new_grid.data = copy.deepcopy(self.data)
        return new_grid
