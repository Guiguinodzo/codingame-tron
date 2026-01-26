import json
import random

HEIGHT = 20
WIDTH = 30

class Config:
    ais: list[AiConfig] = []
    nb_players: int

    def __init__(self, config: dict) -> None:
        self.ais = [AiConfig(ai) for ai in config.get('ais', [])]
        self.nb_players = len(self.ais)

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


class AiConfig:
    program_path: str
    initial_coords: tuple[int, int]

    def __init__(self, config: dict) -> None:
        self.program_path = config['program_path']
        if not self.program_path:
            raise Exception(f"Invalid program_path: {config['program_path']}")
        self.initial_coords = config.get('initial_coords',
                                         (int(random.random() * WIDTH), int(random.random() * HEIGHT)))

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
