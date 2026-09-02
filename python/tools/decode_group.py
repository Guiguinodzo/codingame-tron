import re

import sys

WIDTH=30
HEIGHT=20

def cell_to_xy(cell):
    return (cell % WIDTH), int(cell / WIDTH)

def print(cell_x, cell_y):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            sys.stdout.write(f"{'X' if (cell_x, cell_y) == (x, y) else '.'} ")
        sys.stdout.write(f"\n")

def __main__():
    pattern = re.compile("[A-Z]{2}")
    while True:
        sys.stdout.write(f"Code (ex: WD) ? ")
        line=sys.stdin.readline()[:2].upper()
        if re.match(pattern, line):
            cell=(ord(line[0])-ord("A"))*26 + ord(line[1])-ord("A")
            x, y = cell_to_xy(cell)
            sys.stdout.write(f"{line} = {cell} = ({x}, {y})\n")
            print(x, y)
        else:
            sys.stdout.write(f"Invalid: {line}")

__main__()