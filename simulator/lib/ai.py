import sys
from subprocess import Popen, PIPE
from typing import TextIO

from pexpect import fdpexpect

def log(*args):
    print(*args, file=sys.stderr)

class AI:
    path: str
    process: Popen
    stdout: fdpexpect.fdspawn
    stdin: fdpexpect.fdspawn
    fifo_name: str
    fifo: TextIO

    initial_coords: tuple[int, int]
    running: bool

    def __init__(self, path: str, initial_coords: tuple[int, int]):
        self.path = path
        self.initial_coords = initial_coords

        self.fifo_name = f'fifo{self.initial_coords[0] * 100 + self.initial_coords[1]:04d}'
        self.fifo = open(self.fifo_name, 'w')
        self.process = Popen(['python', path], stdout=PIPE, stdin=PIPE, stderr=self.fifo)
        self.running = True
        self.stdout = fdpexpect.fdspawn(self.process.stdout)
        self.stdin = fdpexpect.fdspawn(self.process.stdin)

    def write_settings(self, nb_players, player_id):
        log(f"Game settings input: {nb_players} {player_id}")
        self.stdin.write(f"{nb_players} {player_id}\n")
        self.stdin.flush()

    def write_player_info(self, p, x0, y0, x1, y1):
        log(f"Input for p={p} : {x0} {y0} {x1} {y1}")
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
