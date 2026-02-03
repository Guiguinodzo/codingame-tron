from ui_module.core.simulator.simulator_interface import SimulatorInterface, OutputBoard, OutputPlayer, InputPlayer
from ui_module.core.simulator.simulator_module.config import Config
from ui_module.core.simulator.simulator_module.simulator import Simulation


class Simulator(SimulatorInterface):

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
            player_config : dict = {
                "program_path": player.ai_path
            }
            if not player.random_pos:
                player_config['initial_coords'] = player.starting_pos

            config["ais"].append(player_config)
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
