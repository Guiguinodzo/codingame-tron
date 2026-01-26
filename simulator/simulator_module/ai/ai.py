import time

from subprocess import Popen, PIPE

from pexpect import fdpexpect

from simulator_module.util.logger import Logger


class AI:
    path: str
    process: Popen
    stdout: fdpexpect.fdspawn
    stdin: fdpexpect.fdspawn

    initial_coords: tuple[int, int]
    player_id: int
    running: bool

    def __init__(self, path: str, initial_coords: tuple[int, int], log_directory: str, logger: Logger):
        self.logger = logger
        self.path = path
        self.initial_coords = initial_coords

        self.log_filename = f'{log_directory}/{self.get_name()}_{time.strftime("%Y%m%d-%H%M%S")}.log'
        self.log_file = open(self.log_filename, 'wb')

        self.process = Popen(['python', path], stdout=PIPE, stdin=PIPE, stderr=self.log_file)
        self.stdout = fdpexpect.fdspawn(self.process.stdout)
        self.stdin = fdpexpect.fdspawn(self.process.stdin)

        self.running = True

    def write_settings(self, nb_players, player_id):
        self.logger.log(f"Game settings input: {nb_players} {player_id}")
        self.player_id = player_id
        self.stdin.write(f"{nb_players} {player_id}\n")
        self.stdin.flush()

    def write_player_info(self, p, x0, y0, x1, y1):
        self.logger.log(f"Input for p={p} : {x0} {y0} {x1} {y1}")
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
        self.process.wait()
        self.log_file.close()
        self.running = False

    def get_name(self):
        return f"{self.path.split('/')[-1].split('.')[0]}_{self.initial_coords[0]:02d}_{self.initial_coords[1]:02d}"
