import sys
import math
from operator import itemgetter
import time

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

HEIGHT=20
WIDTH=30

D_UP    = -WIDTH
D_DOWN  = +WIDTH
D_LEFT  = -1
D_RIGHT = +1

N=-1
P=-1

# config
DEPTH=1

grid=[-1]*HEIGHT*WIDTH
heads=[-1]*4

def to_at(x, y):
    return x + (y * WIDTH)

def to_xy(at):
    return ((at % WIDTH), int(at / WIDTH))

def set_cell(at, p, on_grid=grid):
    on_grid[at]=p

def get_cell(at, from_grid=grid):
    return from_grid[at]

def get_cell_at(at, from_grid=grid):
    return from_grid[at]

# copies grid as if player p goes in direction
def branch_grid(from_grid, from_heads, p, direction):
    new_p_head = from_heads[p] + direction
    return from_grid[0:new_p_head] + [p] + from_grid[new_p_head+1:]


def get_cell_in_direction(at, direction, from_grid=grid):
    return from_grid[at + direction]

def is_direction_valid(at, direction):
    target = at + direction
    if target < 0 or target > HEIGHT*WIDTH:
        return False

    (x,y) = to_xy(at)
    (tx,ty) = to_xy(target)

    return 0 <= tx < WIDTH and 0 <= ty < HEIGHT and ( tx == x or ty == y )

def is_free(at, from_grid=grid):
    return 0 <= at < WIDTH*HEIGHT and get_cell_at(at, from_grid) == -1

def kill(from_grid, player_to_kill):
    return [c if c != player_to_kill else -1 for c in from_grid]


def debug(log):
    print(log, file=sys.stderr, flush=True)

def print_grid(from_grid=grid, from_heads=heads):
    debug("_| " + " ".join([str(i % 10) for i in range(WIDTH)]))
    for y in range(HEIGHT):
        line = f"{y % 10}|"
        for x in range(WIDTH):
            cell = get_cell(to_at(x, y), from_grid)
            cell_str = (
                ('[' if 0 <= cell < len(from_heads) and from_heads[cell] == to_at(x,y) else ' ')
                +
                (str(cell) if cell >= 0 else '.')
                )
            line += cell_str
        debug(line)

def choose(p, from_grid=grid, from_heads=heads) -> int:
    valid_moves = get_valid_moves(from_grid, from_heads, P)
    debug(f"Valid moves: { ', '.join([direction_str(d) for d in valid_moves]) }")

    moves_with_scores : list[tuple[int, int]] = []

    for move in valid_moves:
        (_, score) = evaluate_for_player_after_move(from_grid, from_heads, p, move, 1, DEPTH)
        debug(f"Score if going {direction_str(move)} : {score}")
        moves_with_scores += [ (move, score) ]

    (max_move, max_score) = max(moves_with_scores, key = itemgetter(1))

    debug(f"Best choice: {direction_str(max_move)} ({max_score})")

    return max_move

def get_valid_moves(from_grid, from_heads, p) -> list[int]:
    p_at=heads[p]
    (x,y)=to_xy(p_at)

    #debug(f"p{p} at={p_at} x={x}, y={y}")
    #debug(f'LEFT={is_direction_valid(p_at, D_LEFT)} and {is_free(p_at + D_LEFT)}')
    #debug(f'UP={is_direction_valid(p_at, D_UP)} and {is_free(p_at + D_UP)}')
    #debug(f'RIGHT={is_direction_valid(p_at, D_RIGHT)} and {is_free(p_at + D_RIGHT)}')
    #debug(f'DOWN={is_direction_valid(p_at, D_DOWN)} and {is_free(p_at + D_DOWN)}')

    valid_moves = []
    if is_direction_valid(p_at, D_LEFT) and is_free(p_at + D_LEFT):
        valid_moves += [D_LEFT]
    if is_direction_valid(p_at, D_UP) and is_free(p_at + D_UP):
        valid_moves += [D_UP]
    if is_direction_valid(p_at, D_RIGHT) and is_free(p_at + D_RIGHT):
        valid_moves += [D_RIGHT]
    if is_direction_valid(p_at, D_DOWN) and is_free(p_at + D_DOWN):
        valid_moves += [D_DOWN]

    return valid_moves if len(valid_moves) > 0 else [0]


def evaluate_for_player_after_move(from_grid, from_heads, p, move, coeff=1, depth=0) -> tuple[int, int] :
    p_at=from_heads[p]

    grid_after_move=branch_grid(from_grid, from_heads, p, move)
    heads_after_moves=from_heads[0:p] + [p_at+move] + from_heads[p+1:]
    score_for_move=evaluate_for_player(grid_after_move, heads_after_moves, p, coeff, depth)

    debug(f"{' '*(DEPTH-depth)}Score at move {direction_str(move)} : {score_for_move}, depth={depth}")

    if depth > 0:
        valid_moves=get_valid_moves(from_grid, from_heads, p)

        moves_with_scores : list[tuple[int, int]] = []

        for next_move in valid_moves:
            moves_with_scores += [
                evaluate_for_player_after_move(
                    grid_after_move,
                    heads_after_moves,
                    p,
                    next_move,
                    coeff,
                    depth-1
                )
            ]

        score_for_move += max(moves_with_scores, key = itemgetter(1))[1]

    return (move, score_for_move)

def evaluate_for_player(from_grid, from_heads, p, coeff=1, depth=0) -> int :
    valid_moves=get_valid_moves(from_grid, from_heads, p)

    score = 0
    for move in valid_moves:
        score += count_accessible(from_grid.copy(), from_heads[p] + move)

    return score * coeff

def count_accessible(counting_grid, origin, depth=10) -> int :
    counting_grid[origin]=9

    free_neighbours = []
    if is_direction_valid(origin, D_LEFT) and is_free(origin + D_LEFT, counting_grid):
        free_neighbours += [origin + D_LEFT]

    if is_direction_valid(origin, D_UP) and is_free(origin + D_UP, counting_grid):
        free_neighbours += [origin + D_UP]

    if is_direction_valid(origin, D_RIGHT) and is_free(origin + D_RIGHT, counting_grid):
        free_neighbours += [origin + D_RIGHT]

    if is_direction_valid(origin, D_DOWN) and is_free(origin + D_DOWN, counting_grid):
        free_neighbours += [origin + D_DOWN]

    count = len(free_neighbours)

    if (depth > 0) :
        for next in free_neighbours:
            counting_grid[next] = 9

        for next in free_neighbours:
            count += count_accessible(counting_grid, next, depth-1)

    if depth==10 :
        print_grid(counting_grid)

    return count



def print_direction(direction):
    print(direction_str(direction))

def direction_str(direction):
    return (
        'LEFT' if direction == D_LEFT else
        'UP' if direction == D_UP else
        'RIGHT' if direction == D_RIGHT else
        'DOWN' if direction == D_DOWN else
        'ERROR'
        )

# game loop
while True:
    # n: total number of players (2 to 4).
    # p: your player number (0 to 3).
    n, p = [int(i) for i in input().split()]
    N=n
    P=p
    debug(f"I am p{p}")
    heads=[-1]*N
    for i in range(n):
        # x0: starting X coordinate of lightcycle (or -1)
        # y0: starting Y coordinate of lightcycle (or -1)
        # x1: starting X coordinate of lightcycle (can be the same as X0 if you play before this player)
        # y1: starting Y coordinate of lightcycle (can be the same as Y0 if you play before this player)
        x0, y0, x1, y1 = [int(j) for j in input().split()]

        if x0 == -1:
            debug(f"Killing p{i}")
            grid = kill(grid, i)
            heads[i]=-1
            print_grid(grid)
        else:
            at1=to_at(x1, y1)
            set_cell(at1, i)
            heads[i]=at1

            debug(f"p{i} {x1},{y1}={i} (grid = {get_cell(at1)})")

    #print_grid()

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # A single line with UP, DOWN, LEFT or RIGHT
    time_before = time.time()
    direction = choose(p)
    time_after = time.time()

    debug(f"Going {direction_str(direction)} (time: {((time_after - time_before) * 1000):.3f} ms)")
    #print_grid(branch_grid(grid, heads, P, direction))



    print_direction(direction)
