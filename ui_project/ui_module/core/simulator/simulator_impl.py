import simulator_module.simulator

from ui_module.core.simulator.simulator_interface import SimulatorInterface, OutputBoard, InputPlayer


class Simulator(SimulatorInterface):

    simulation: simulator_module.simulator.Simulation

    def __init__(self):
        pass

    def start_simulation(self, players: list[InputPlayer]):



        pass

    def get_total_step_number(self) -> int:
        pass

    def get_board_at(self, step: int) -> OutputBoard:
        pass

    def get_player_stdout_at(self, step: int, player_id: int) -> str:
        pass

    def get_player_stderr_at(self, step: int, player_id: int) -> str:
        pass

    def get_winner(self) -> int:
        pass

    def get_player_death_step(self, player_id: int) -> int:
        pass