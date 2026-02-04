import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import QObject, Signal, QThread, Slot

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

class MetaSimulatorInterface(type(QObject), type(ABC)):
    pass

class SimulatorInterface(QObject, ABC, metaclass=MetaSimulatorInterface):
    class SimulationWorker(QObject):
        finished = Signal()
        advancement = Signal(float)

        def __init__(self, simulator: "SimulatorInterface", players):
            super().__init__()
            self.simulator = simulator
            self.players = players

        @Slot()
        def run(self):
            self.simulator._start_simulation(self.players)
            self.finished.emit()

    # Signals
    advancement = Signal(float)     # The value should be in [float(0), float(100)].
    finished = Signal()             # Send this signal when the simulation is ready for all the abstract methods (except for start_simulation).

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._worker = None

    @abstractmethod
    def _start_simulation(self, players: list[InputPlayer]):
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

    def start_simulation(self, players: list[InputPlayer]):
        self._thread = QThread(self)
        self._worker = self.SimulationWorker(self, players)

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self.finished)
        self._worker.finished.connect(self._thread.quit)

        self._worker.advancement.connect(self.advancement)

        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()