import json
import random
import sys
import traceback
from subprocess import Popen, PIPE
from time import sleep

from pexpect import fdpexpect

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
    initial_coords: list[tuple[int, int]]
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
        self.initial_coords = initial_coords
        self.heads = [(0, 0)]*self.nb_players
        for (p, (x, y)) in enumerate(self.initial_coords):
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
            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    if self.grid.get(x,y) == player:
                        self.grid.set(x, y, -1)
            return False

    def get_initial_coords(self, player):
        return self.initial_coords[player] if not self.is_dead(player) else (-1, -1)

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

class AI:
    path: str
    process: Popen
    stdout: fdpexpect.fdspawn
    stderr: fdpexpect.fdspawn
    stdin: fdpexpect.fdspawn

    initial_coords: tuple[int, int]
    running: bool

    def __init__(self, path: str, initial_coords: tuple[int, int]):
        self.path = path
        self.process = Popen(['python', path], stdout=PIPE, stdin=PIPE)
        self.running = True
        self.stdout = fdpexpect.fdspawn(self.process.stdout)
        self.stdin = fdpexpect.fdspawn(self.process.stdin)
        self.initial_coords = initial_coords

    def write_settings(self, nb_players, player_id):
        print(f"Game settings input: {nb_players} {player_id}")
        self.stdin.write(f"{nb_players} {player_id}\n")
        self.stdin.flush()

    def write_player_info(self, p, x0, y0, x1, y1):
        print(f"Input for p={p} : {x0} {y0} {x1} {y1}")
        self.stdin.write(f"{x0} {y0} {x1} {y1}\n")
        self.stdin.flush()

    def read_move(self):
        moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        index = self.stdout.expect(moves, timeout=None)
        return moves[index]

    def stop(self):
        if not self.running:
            return
        self.process.kill()
        self.running = False

class Config:
    ais: list[AiConfig] = []
    nb_players: int

    def __init__(self, config: dict) -> None:
        self.ais = [ AiConfig(ai) for ai in config.get('ais', [])]
        self.nb_players = len(self.ais)

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

class AiConfig:
    program_path: str
    initial_coords: tuple[int, int]

    def __init__(self, config: dict) -> None:
        self.program_path = config['program_path']
        if not self.program_path:
            raise Exception(f"Invalid program_path: {config['program_path']}")
        self.initial_coords = config.get('initial_coords', (int(random.random()*WIDTH), int(random.random()*HEIGHT)))

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


def main():

    ais : list[AI] = []

    try:
        args = sys.argv[1:]

        config = Config({
            "ais": [
                {
                    "program_path": "./mockai.py",
                },
                {
                    "program_path": "./mockai.py",
                },
                {
                    "program_path": "./mockai.py",
                },
                {
                    "program_path": "./mockai.py",
                }
            ]
        })
        if len(args)>0:
            config_file_path = args[0]
            with open(config_file_path, 'r') as config_file:
                json_config = json.load(config_file)
                config = Config(json_config)

        print(f"Config: {config}")

        for (player, ai_config) in enumerate(config.ais):
            print(ai_config.program_path)
            ais.append(AI(ai_config.program_path, ai_config.initial_coords))

        game = Game([ai.initial_coords for ai in ais])
        game.print()

        while game.winner() == -1:
            for player in range(game.nb_players):
                if game.winner() != -1:
                    continue

                if game.is_dead(player):
                    print(f'Player {player} is dead')
                    ais[player].stop()
                    continue

                ais[player].write_settings(game.nb_players, player)

                for p in range(game.nb_players):
                    (x1, y1) = game.get_head(p)
                    (x0, y0) = game.get_initial_coords(p)
                    ais[player].write_player_info(p, x0, y0, x1, y1)

                player_move = ais[player].read_move()
                print(f'Move for player {player} : {player_move}')

                game.move_player(player, player_move)
            game.print()
            sleep(0.5)
            # input("Press any key to continue...")

        print(f"Game over. Winner: {game.winner()}")

    except Exception:
        print(traceback.format_exc())
        sys.exit(1)
    finally:
        if ais:
            for ai in ais:
                ai.stop()


if __name__ == "__main__":
    main()

