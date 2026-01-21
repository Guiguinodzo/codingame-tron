import sys
import traceback
from operator import truediv

import pexpect

HEIGHT = 20

WIDTH = 30


class Grid:

    width: int
    height: int
    data: list[list[int]]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [ ([-1]*height) for _ in range(width) ]

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



class Game:

    nb_players: int
    grid: Grid
    heads: list[tuple[int, int]]
    moves = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0)
    }


    def __init__(self, initial_coords: list[tuple[int, int]]):
        self.nb_players = len(initial_coords)
        self.grid = Grid(WIDTH, HEIGHT)
        self.heads = [(0, 0)]*self.nb_players
        for (p, (x, y)) in enumerate(initial_coords):
            self.grid.set(x, y, p)
            self.heads[p] = (x, y)

    def move_player(self, player, move: str) -> bool:
        (x, y) = self.heads[player]
        (dx, dy) = self.moves[move]
        if self.grid.is_valid(x+dx, y+dy) and self.grid.get(x+dx, y+dy) == -1:
            self.grid.set(x+dx, y+dy, player)
            self.heads[player] = (x+dx, y+dy)
            return True
        else:
            print(f'Invalid move: {move} : killing {player}')
            self.heads[player] = (-1, -1)
            return False

    def get_head(self, player) -> tuple[int, int]:
        return self.heads[player]

    def is_dead(self, player) -> bool:
        return self.heads[player] == (-1, -1)

    def winner(self) -> int:
        alive_players = [ p for p, (x, y) in enumerate(self.heads) if (x, y) != (-1, -1)]
        return alive_players[0] if len(alive_players) == 1 else -1

    def print(self):
        header = "_| " + " ".join([str(i % 10) for i in range(self.grid.width)])
        print(header)
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
            print(line)



def main():
    try:
        programs_paths = sys.argv[1:]

        initial_coords = [
            (4, 4),
            (4, 14),
            (24, 4),
            (24, 14)
        ]

        ais = []
        for (player, program_path) in enumerate(programs_paths):
            print(program_path)
            ais.append(pexpect.spawn(f"python {program_path}"))

        game = Game(initial_coords[0:len(ais)])
        game.print()

        moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        while game.winner() == -1:
            for player in range(game.nb_players):
                if game.winner() != -1:
                    continue

                if game.is_dead(player):
                    print(f'Player {player} is dead')
                    continue

                game_settings_input = f"{game.nb_players} {player}"
                ais[player].sendline(game_settings_input)
                print(f"Game settings input: {game_settings_input}")
                for p in range(game.nb_players):
                    (x1, y1) = game.get_head(p)
                    (x0, y0) = initial_coords[p] if not game.is_dead(p) else (-1, -1)
                    p_input = f"{x0} {y0} {x1} {y1}"
                    ais[player].sendline(p_input)
                    print(f"Input for p={p} : {p_input}")

                move_index = ais[player].expect([m[0] for m in moves])

                player_move = moves[move_index]
                print(f'Move for player {player} : {player_move}')
                game.move_player(player, player_move)
            game.print()
            input("Press Enter to continue...")

        print(f"Game over. Winner: {game.winner()}")

    except Exception:
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

