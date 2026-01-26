from copy import deepcopy
from typing import Self

from simulator_module.game.grid import Grid
from simulator_module.util.logger import Logger

HEIGHT = 20
WIDTH = 30
MOVES = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

class Game:

    _nb_players: int
    _initial_coords: list[tuple[int, int]]
    _states: list[GameState]

    def __init__(self, initial_coords: list[tuple[int, int]], logger: Logger):
        self.logger = logger
        self._nb_players = len(initial_coords)
        self._initial_coords = initial_coords

        grid = Grid(WIDTH, HEIGHT)
        heads = [(0, 0)] * self._nb_players
        for (p, (x, y)) in enumerate(self._initial_coords):
            grid.set(x, y, p)
            heads[p] = (x, y)
        self._states = [GameState(grid, heads)]

    def get_nb_players(self):
        return self._nb_players

    def get_initial_coords(self):
        return self._initial_coords

    def get_states(self):
        return self._states

    def get_last_state(self):
        return self._states[-1]

    def move_player(self, player, move: str) -> GameState:
        last_state = self._states[-1]
        next_state = last_state.move_player(player, move)
        self._states.append(next_state)
        return next_state

    def get_player_initial_coords(self, player):
        return self._initial_coords[player] if not self._states[-1].is_dead(player) else (-1, -1)


class GameState:

    def __init__(self, grid: Grid, heads: list[tuple[int, int]], current_player: int|None = None, turn: int = 0, previous: Self = None):
        self._grid = grid
        self._heads = heads
        self._current_player = current_player
        self._turn = turn
        self._previous = previous

    def get_grid(self):
        return self._grid

    def get_heads(self):
        return self._heads

    def get_current_player(self):
        return self._current_player

    def get_turn(self):
        return self._turn

    def get_alive_players(self):
        return [player for (player, heads) in enumerate(self._heads) if heads != (-1, -1)]

    def get_head(self, player) -> tuple[int, int]:
        return self._heads[player]

    def is_dead(self, player) -> bool:
        return self._heads[player] == (-1, -1)

    def winner(self) -> int:
        alive_players = [p for p, (x, y) in enumerate(self._heads) if (x, y) != (-1, -1)]
        return alive_players[0] if len(alive_players) == 1 else -1

    def get_player_path(self, player) -> list[tuple[int,int]]:
        player_head = self._heads[player]
        if player_head == (-1, -1):
            return []
        elif self._previous is None:
            return [player_head]
        else:
            return self._previous.get_player_path(player) + [player_head]

    def move_player(self, player, move: str) -> Self:
        (x, y) = self._heads[player]
        (dx, dy) = MOVES[move]

        next_grid = deepcopy(self._grid)
        next_heads = self._heads[:]

        if self._grid.is_valid(x + dx, y + dy) and self._grid.get(x + dx, y + dy) == -1:
            next_grid.set(x + dx, y + dy, player)
            next_heads[player] = (x + dx, y + dy)
        else:
            next_heads[player] = (-1, -1)
            next_grid.replace(player, -1)

        return GameState(next_grid, next_heads, player, self._turn + 1, self)

    def print(self, logger: Logger):
        header = "_| " + " ".join([str(i % 10) for i in range(self._grid.width)])
        logger.log(header)
        for y in range(self._grid.height):
            line = f"{y % 10}|"
            for x in range(self._grid.width):
                value = self._grid.get(x, y)
                cell_str = (
                        ('[' if 0 <= value and self._heads[value] == (x, y) else ' ')
                        +
                        (str(value) if value >= 0 else '.')
                )
                line += cell_str
            logger.log(line)
