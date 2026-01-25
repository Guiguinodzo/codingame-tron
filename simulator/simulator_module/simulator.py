import json
import os
import sys
import time
import traceback
from typing import Callable

from simulator_module.ai.ai import AI
from simulator_module.config import Config
from simulator_module.game.game import Game
from simulator_module.util.logger import Logger

HEIGHT = 20
WIDTH = 30

log_directory = f'logs/run_{time.strftime("%Y%m%d-%H%M%S")}'
os.mkdir(log_directory)
LOGGER = Logger(f'{log_directory}/simulator.log')

class Simulation:

    def __init__(self, config: Config, logger):
        self.config = config
        self.logger = logger
        self.logger.log(f"Config: {config}")

        self.ais: list[AI] = []
        for (player, ai_config) in enumerate(config.ais):
            self.logger.log(ai_config.program_path)
            self.ais.append(AI(ai_config.program_path, ai_config.initial_coords, log_directory, self.logger))

        self.game = Game([ai.initial_coords for ai in self.ais], self.logger)


    def start(self, progress_callback: Callable[[int, int, str],None] = None):
        self.logger.log("Starting simulation")
        turn = 0
        if progress_callback:
            progress_callback(turn, -1, "start")
        while self.game.winner() == -1:
            for player in range(self.game.nb_players):
                if self.game.winner() != -1:
                    continue

                if self.game.is_dead(player):
                    self.ais[player].stop()
                    turn +=1
                    if progress_callback:
                        progress_callback(turn, player, "death")
                    continue

                self.ais[player].write_settings(self.game.nb_players, player)

                for p in range(self.game.nb_players):
                    (x1, y1) = self.game.get_head(p)
                    (x0, y0) = self.game.get_initial_coords(p)
                    self.ais[player].write_player_info(p, x0, y0, x1, y1)

                player_move = self.ais[player].read_move()
                self.game.move_player(player, player_move)

                turn += 1
                if progress_callback:
                    progress_callback(turn, player, player_move)

        turn = 600 # max turn is 598
        if progress_callback:
            progress_callback(turn, self.game.winner(), "win")

    def stop(self):
        for ai in self.ais:
            ai.stop()


def progress_function(logger) -> Callable[[int, int, str],None]:
    return lambda turn, player, move : logger.log(f"Progress {turn} / 600 = {turn/6:.2f}% : player #{player} -> {move}")


def main():

    simulation: Simulation|None = None
    exit_code = 0

    try:
        args = sys.argv[1:]

        config = Config({
            "ais": [
            ]
        })
        if len(args) > 0:
            config_file_path = args[0]
            with open(config_file_path, 'r') as config_file:
                json_config = json.load(config_file)
                config = Config(json_config)

        LOGGER.log(f"Config: {config}")

        simulation = Simulation(config, LOGGER)
        simulation.start(progress_function(LOGGER))



    except Exception:
        LOGGER.log(traceback.format_exc())
        exit_code=1
    finally:
        if simulation:
            simulation.stop()
        LOGGER.close()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
