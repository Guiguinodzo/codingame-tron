from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from PySide6.QtCore import QObject, Signal

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

    def __init__(self, parent=None):
        super().__init__(parent)

    @abstractmethod
    def start_simulation(self, players: list[InputPlayer]):
        pass

    @abstractmethod
    def get_total_step_number(self) -> int:
        pass

    @abstractmethod
    def get_board_at(self, step: int) -> OutputBoard:
        pass

    @abstractmethod
    def get_player_stdout_at(self, step: int, player_id: int) -> str:
        pass

    @abstractmethod
    def get_player_stderr_at(self, step: int, player_id: int) -> str:
        pass

    @abstractmethod
    def get_winner(self) -> int:    # return winner's player_id
        pass

    @abstractmethod
    def get_player_death_step(self, player_id: int) -> int:
        pass