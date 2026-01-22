from lib.game import Game


class GameBox:
    width: int
    height: int
    game: Game
    def __init__(self, stdscr, game: Game, x: int, y: int) -> None:
        self.stdscr = stdscr
        self.game = game
        self.width = game.grid.width
        self.height = game.grid.height
        self.x = x
        self.y = y


