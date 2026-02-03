import json
import os
import sys
import time
import traceback
from typing import Callable

from ui_module.core.simulator.simulator_module.ai.ai import AI
from ui_module.core.simulator.simulator_module.config import Config
from ui_module.core.simulator.simulator_module.game.game import Game
from ui_module.core.simulator.simulator_module.util.logger import Logger

from enum import Enum

HEIGHT = 20
WIDTH = 30

log_directory = f'logs/run_{time.strftime("%Y%m%d-%H%M%S")}'
os.makedirs(log_directory, exist_ok=True)
LOGGER = Logger(f'{log_directory}/simulator.log')

class SimulationState(Enum):
    INITIALIZED = 0
    RUNNING = 1
    COMPLETED = 2


class Simulation:

    _state: SimulationState = SimulationState.INITIALIZED

    def __init__(self, config: Config, logger = LOGGER):
        self._config = config
        self._logger = logger
        self._logger.log(f"Config: {config}")

        self.ais: list[AI] = []
        for (player, ai_config) in enumerate(config.ais):
            self._logger.log(ai_config.program_path)
            self.ais.append(AI(player, ai_config.program_path, ai_config.initial_coords, log_directory, self._logger))

        self.game = Game([ai.initial_coords for ai in self.ais], self._logger)

    def get_state(self) -> SimulationState:
        return self._state

    def start(self, progress_callback: Callable[[int, int, str],None] = None):
        self._logger.log("Starting simulation")
        self._state = SimulationState.RUNNING
        turn = 0
        if progress_callback:
            progress_callback(turn, -1, "start")

        while self.game.get_last_state().winner() == -1:
            for player in range(self.game.get_nb_players()):
                if self.game.get_last_state().winner() != -1:
                    continue

                if self.game.get_last_state().is_dead(player):
                    self.ais[player].stop()
                    turn +=1
                    if progress_callback:
                        progress_callback(turn, player, "death")
                    continue

                self.ais[player].write_settings(self.game.get_nb_players())

                for p in range(self.game.get_nb_players()):
                    (x1, y1) = self.game.get_last_state().get_head(p)
                    (x0, y0) = self.game.get_player_initial_coords(p)
                    self.ais[player].write_player_info(p, x0, y0, x1, y1)

                player_move = self.ais[player].read_move()
                self.game.move_player(player, player_move).print(self._logger)

                turn += 1
                if progress_callback:
                    progress_callback(turn, player, player_move)

        self._state = SimulationState.COMPLETED
        turn = 950 # max turn is 950
        if progress_callback:
            progress_callback(turn, self.game.get_last_state().winner(), "win")

    def stop(self):
        for ai in self.ais:
            ai.stop()

    def print_all_states(self):
        for state in self.game.get_states():
            self._logger.log(f"Turn: {state.get_turn()}  - Player: #{state.get_current_player()}")
            state.print(self._logger)


def progress_function(logger) -> Callable[[int, int, str],None]:
    return lambda turn, player, move : logger.log(f"Progress {turn} / 950 = {turn/9.5:.2f}% : player #{player} -> {move}")


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

        input("Press any key to print all states...")
        simulation.print_all_states()

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
