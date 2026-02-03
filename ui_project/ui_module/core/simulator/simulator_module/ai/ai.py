import time

from subprocess import Popen, PIPE

from pexpect import fdpexpect

from ui_module.core.simulator.simulator_module.util.logger import Logger


class AI:
    path: str
    process: Popen
    stdout: fdpexpect.fdspawn
    stdin: fdpexpect.fdspawn

    initial_coords: tuple[int, int]
    player_id: int
    running: bool

    def __init__(self, player_id, path: str, initial_coords: tuple[int, int], log_directory: str, logger: Logger):
        self.player_id = player_id
        self.logger = logger
        self.path = path
        self.initial_coords = initial_coords
        self.enabled = self.initial_coords != (-1, -1)
        self.log_filename = f'{log_directory}/{self.get_name()}.log'
        self.log_file = open(self.log_filename, 'wb')

        if self.enabled:
            self.process = Popen(['python', path], stdout=PIPE, stdin=PIPE, stderr=self.log_file)
            self.stdout = fdpexpect.fdspawn(self.process.stdout)
            self.stdin = fdpexpect.fdspawn(self.process.stdin)

            self.running = True
        else: # disabled ai
            self.running = False

    def write_settings(self, nb_players):
        if not self.running:
            self.logger.log(f"Cannot write settings because AI {self.player_id} is not running")
            return

        self.logger.log(f"Game settings input: {nb_players} {self.player_id}")
        self.stdin.write(f"{nb_players} {self.player_id}\n")
        self.stdin.flush()

    def write_player_info(self, p, x0, y0, x1, y1):
        if not self.running:
            self.logger.log(f"Cannot write player info because AI {self.player_id} is not running")
            return
        self.logger.log(f"Input for p={p} : {x0} {y0} {x1} {y1}")
        self.stdin.write(f"{x0} {y0} {x1} {y1}\n")
        self.stdin.flush()

    def read_move(self):
        if not self.running:
            self.logger.log(f"Cannot read move because AI {self.player_id} is not running, defaults to DOWN")
            return 'DOWN'

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
        return f"{self.player_id}_{self.path.split('/')[-1].split('.')[0]}" if self.enabled else f"{self.player_id}_disabled"
