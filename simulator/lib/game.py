from lib.display import Display
from lib.grid import Grid
from lib.logger import Logger

HEIGHT = 20
WIDTH = 30

class Game:
    nb_players: int
    grid: Grid
    initial_coords: list[tuple[int, int]]
    heads: list[tuple[int, int]]
    moves = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0)
    }

    def __init__(self, initial_coords: list[tuple[int, int]], logger: Logger):
        self.logger = logger
        self.nb_players = len(initial_coords)
        self.grid = Grid(WIDTH, HEIGHT)
        self.initial_coords = initial_coords
        self.heads = [(0, 0)] * self.nb_players
        for (p, (x, y)) in enumerate(self.initial_coords):
            self.grid.set(x, y, p)
            self.heads[p] = (x, y)

    def move_player(self, player, move: str) -> bool:
        (x, y) = self.heads[player]
        (dx, dy) = self.moves[move]
        if self.grid.is_valid(x + dx, y + dy) and self.grid.get(x + dx, y + dy) == -1:
            self.grid.set(x + dx, y + dy, player)
            self.heads[player] = (x + dx, y + dy)
            return True
        else:
            self.logger.log(f'Invalid move: {move} : killing {player}')
            self.heads[player] = (-1, -1)
            self.grid.replace(player, -1)
            return False

    def get_initial_coords(self, player):
        return self.initial_coords[player] if not self.is_dead(player) else (-1, -1)

    def get_head(self, player) -> tuple[int, int]:
        return self.heads[player]

    def is_dead(self, player) -> bool:
        return self.heads[player] == (-1, -1)

    def winner(self) -> int:
        alive_players = [p for p, (x, y) in enumerate(self.heads) if (x, y) != (-1, -1)]
        return alive_players[0] if len(alive_players) == 1 else -1

    def print(self):
        header = "_| " + " ".join([str(i % 10) for i in range(self.grid.width)])
        self.logger.log(header)
        for y in range(self.grid.height):
            line = f"{y % 10}|"
            for x in range(self.grid.width):
                value = self.grid.get(x, y)
                cell_str = (
                        ('[' if 0 <= value < self.nb_players and self.heads[value] == (x, y) else ' ')
                        +
                        (str(value) if value >= 0 else '.')
                )
                line += cell_str
            self.logger.log(line)

    def print_in_display(self, display: Display):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                value = self.grid.get(x, y)
                if value >= 0:
                    display.write(x, y, value)
        display.refresh()
