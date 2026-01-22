import curses
import random
from curses import wrapper

MARGIN_LEFT = 10
MARGIN_TOP = 10

BORDER_VERTICAL = '\u2551'
BORDER_HORIZONTAL = '\u2550'
CORNER_TOP_LEFT = '\u2554'
CORNER_TOP_RIGHT = '\u2557'
CORNER_BOTTOM_LEFT = '\u255A'
CORNER_BOTTOM_RIGHT = '\u255D'

DOT = '\u2586'

WIDTH = 30
HEIGHT = 20


class Display:
    pairs: dict[int, int] = {}

    def __init__(self, stdscr):
        self.stdscr = stdscr

        self.define_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
        self.define_pair(2, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        self.define_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        self.define_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)

    def clear(self):
        self.stdscr.clear()

    def draw_frame(self, margin_left, margin_top, width, height, with_indexes=False):
        if with_indexes:
            x_abscissa = "".join([str(i % 10) for i in range(width)])
            self.stdscr.addstr(margin_top - 2, margin_left, x_abscissa)
            for i in range(height):
                self.stdscr.addstr(margin_top + i, margin_left - 2, str(i % 10))

        line_with_border = BORDER_VERTICAL + (" " * width) + BORDER_VERTICAL
        top_border = CORNER_TOP_LEFT + (BORDER_HORIZONTAL * width) + CORNER_TOP_RIGHT
        bottom_border = CORNER_BOTTOM_LEFT + (BORDER_HORIZONTAL * width) + CORNER_BOTTOM_RIGHT

        self.stdscr.addstr(margin_top - 1, margin_left - 1, top_border)
        for y in range(height):
            self.stdscr.addstr(margin_top + y, margin_left - 1, line_with_border)
        self.stdscr.addstr(margin_top + height, margin_left - 1, bottom_border)

    def define_pair(self, i, fg, bg):
        curses.init_pair(i, fg, bg)
        self.pairs[i - 1] = curses.color_pair(i)

    def write(self, x, y, text, color=None):
        self.stdscr.addstr(y, x, text, self.pairs.get(color, 1))

    def refresh(self):
        self.stdscr.refresh()

    def wait_for_key(self):
        return self.stdscr.getch()


def main(stdscr):
    display = Display(stdscr)

    display.clear()
    display.draw_frame(MARGIN_LEFT, MARGIN_TOP, WIDTH, HEIGHT)
    display.refresh()

    while stdscr.getch() != ord('q'):
        display.write(
            MARGIN_LEFT + int(random.random() * WIDTH),
            MARGIN_TOP + int(random.random() * HEIGHT),
            str(int(random.random() * 4)),
            int(random.random() * 4)
        )
        display.refresh()


if __name__ == "__main__":
    wrapper(main)
