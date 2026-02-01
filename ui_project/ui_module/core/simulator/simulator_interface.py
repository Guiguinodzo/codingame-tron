from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import QObject, Signal
from simulator_module.config import Config
from simulator_module.simulator import Simulation


@dataclass
class InputPlayer:
    id: int                         # 0 <= id < 4
    ai_path: str
    random_pos: bool                # If true starting_pos will be None value
    starting_pos: Optional[tuple[int, int]]   # Two players will never have the same starting_pos value

@dataclass
class OutputPlayer:
    id: int
    head: tuple[int, int]
    trail: list[tuple[int, int]] = field(default_factory=list)

@dataclass
class OutputBoard:
    players: list[OutputPlayer] = field(default_factory=list)

class SimulatorInterface(QObject, ABC):

    # Signals
    advancement = Signal(float)     # The value should be in [float(0), float(1)].
    finished = Signal()             # Send this signal when the simulation is ready for all the abstract methods (except for start_simulation).

    simulation: Simulation

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui_to_simulator_player_mapping = {}
        self.simulator_to_ui_player_mapping = {}

    def start_simulation(self, players: list[InputPlayer]):
        self.ui_to_simulator_player_mapping = {}
        self.simulator_to_ui_player_mapping = {}
        config = {
            "ais": []
        }
        for index, player in enumerate(players):
            config["ais"].append({
                "program_path": player.ai_path,
                "initial_coords": player.starting_pos if not player.random_pos else None
            })
            self._map_user(player.id, index)

        self.simulation = Simulation(Config(config))
        self.simulation.start(lambda turn, _, _2 : self.advancement.emit(turn/9.5))
        self.finished.emit()

    def _map_user(self, player_ui_id: int, player_simulator_id: int):
        self.ui_to_simulator_player_mapping[player_ui_id] = player_simulator_id
        self.simulator_to_ui_player_mapping[player_simulator_id] = player_ui_id

    def get_total_step_number(self) -> int:
        return len(self.simulation.game.get_states())

    def get_board_at(self, step: int) -> OutputBoard:
        state_at_step = self.simulation.game.get_states()[step]
        output_board = OutputBoard()
        for player_ui_id, player_id in self.ui_to_simulator_player_mapping.items():
            head = state_at_step.get_head(player_id)
            trail = state_at_step.get_player_path(player_id)
            output_board.players.append(OutputPlayer(player_ui_id, head, trail))

        return output_board

    def get_player_stdout_at(self, step: int, player_id: int) -> str:
        return f"Not implemented yet: get_player_stdout_at({step}, {player_id})"

    def get_player_stderr_at(self, step: int, player_id: int) -> str:
        return f"Not implemented yet: get_player_stderr_at({step}, {player_id})"

    def get_winner(self) -> int:    # return winner's player_id
        winner_id = self.simulation.game.get_winner()
        if winner_id == -1:
            return -1
        else:
            return self.simulator_to_ui_player_mapping.get(winner_id)

    def get_player_death_step(self, player_id: int) -> int:
        player_simulator_id = self.ui_to_simulator_player_mapping.get(player_id)
        if player_simulator_id is None:
            return -1

        states = self.simulation.game.get_states()
        index = len(states) - 1
        while index >= 0 and not states[index].is_dead(player_simulator_id):
            index -= 1

        return index