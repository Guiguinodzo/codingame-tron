import json
import sys
import traceback

from lib.ai import AI
from lib.config import Config
from lib.game import Game

HEIGHT = 20
WIDTH = 30


class OutputWrapper:
    text = ""

    def write(self, txt):
        self.text += txt

    def get_text(self, beg = None, end = None):
        return '\n'.join(self.text.split('\n')[beg:end])


def log(*args):
    print(*args, file=sys.stderr)


def main(stdscr = None):
    output_wrapper = OutputWrapper()
    # sys.stderr = output_wrapper

    # display = Display(stdscr)

    ais: list[AI] = []

    try:
        args = sys.argv[1:]

        config = Config({
            "ais": [
                {
                    "program_path": "./mockai.py",
                },
                {
                    "program_path": "./mockai.py",
                },
                {
                    "program_path": "./mockai.py",
                },
                {
                    "program_path": "./mockai.py",
                }
            ]
        })
        if len(args) > 0:
            config_file_path = args[0]
            with open(config_file_path, 'r') as config_file:
                json_config = json.load(config_file)
                config = Config(json_config)

        log(f"Config: {config}")

        for (player, ai_config) in enumerate(config.ais):
            log(ai_config.program_path)
            ais.append(AI(ai_config.program_path, ai_config.initial_coords))

        game = Game([ai.initial_coords for ai in ais])
        # game.print()

        while game.winner() == -1:
            for player in range(game.nb_players):
                if game.winner() != -1:
                    continue

                if game.is_dead(player):
                    log(f'Player {player} is dead')
                    ais[player].stop()
                    continue

                ais[player].write_settings(game.nb_players, player)

                for p in range(game.nb_players):
                    (x1, y1) = game.get_head(p)
                    (x0, y0) = game.get_initial_coords(p)
                    ais[player].write_player_info(p, x0, y0, x1, y1)

                player_move = ais[player].read_move()
                log(f'Move for player {player} : {player_move}')

                game.move_player(player, player_move)

            # display.clear()
            # display.draw_frame(WIDTH, HEIGHT)
            # game.print_in_display(display)
            # display.refresh()
            # sleep(0.1)
            # display.wait_for_key()

            game.print()

        log(f"Game over. Winner: {game.winner()}")

        # sys.stderr = sys.__stderr__

        for line in output_wrapper.get_text():
            log(line)

    except Exception:
        log(traceback.format_exc())
        sys.exit(1)
    finally:
        if ais:
            for ai in ais:
                ai.stop()


if __name__ == "__main__":
    # wrapper(main)
    main()
