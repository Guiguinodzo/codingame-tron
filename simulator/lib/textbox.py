
import curses
from curses import wrapper
from random import random

from display import Display


class Textbox:


    def __init__(self, stdscr, display, col_position, row_position, width, height):
        self.stdscr = stdscr
        self.display = display

        self.col_position = col_position
        self.row_position = row_position
        self.width = width
        self.height = height

        self.pad = curses.newpad(32000, self.width)

        self.lines = []
        self.row = 0
        self.col = 0

    def draw(self):
        self.display.draw_frame(self.row_position - 1, self.col_position - 1, self.width + 2, self.height + 2)
        self.refresh()

    def refresh(self):
        self.pad.refresh(
            self.row, self.col,
            self.row_position, self.col_position,
            self.height + self.row_position, self.width + self.col_position
        )

    def scroll_down(self):
        self.row = min(self.row + 1, self.height)
        self.refresh()

    def scroll_up(self):
        self.row = max(self.row - 1, 0)
        self.refresh()

    def scroll_left(self):
        self.col = max(self.col - 1, 0)
        self.refresh()

    def scroll_right(self):
        self.col = min(self.col + 1, self.width)
        self.refresh()

    def add_line(self, line):
        # split lines?
        self.lines.append(line)
        self.pad.addstr(len(self.lines)-1, 0, line)
        self.refresh()




def main(stdscr):
    display = Display(stdscr)
    display.clear()

    textbox = Textbox(stdscr, display, 10, 10, 120, 5)
    textbox.draw()
    lipsum_words = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce posuere enim sit amet commodo molestie. Aliquam quis lacus vestibulum, tempus ipsum non, eleifend libero.".split(" ")

    generate_lipsum = lambda n: " ".join(lipsum_words[int(random() * len(lipsum_words))] for _ in range(n))


    for _ in range(100):
        textbox.add_line(generate_lipsum(int(random()*15)+1))
        textbox.refresh()

    running = True
    while running:
        key = stdscr.getch()
        if key == ord('q'):
            running = False
        elif key == curses.KEY_DOWN:
            textbox.scroll_down()
        elif key == curses.KEY_UP:
            textbox.scroll_up()
        elif key == curses.KEY_LEFT:
            textbox.scroll_left()
        elif key == curses.KEY_RIGHT:
            textbox.scroll_right()


if __name__ == "__main__":
    wrapper(main)
