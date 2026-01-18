import sys
import math
from operator import itemgetter
import time
from functools import reduce

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

LOG_DEBUG=0
LOG_INFO=1
LOG_WARN=2
LOG_ERROR=3

LOG_THRESHOLD=LOG_INFO

HEIGHT=20
WIDTH=30

D_UP    = -WIDTH
D_DOWN  = +WIDTH
D_LEFT  = -1
D_RIGHT = +1

NB_PLAYERS=-1
P=-1

# config
DEPTH=10
MAX_TIME_RATIO=0.95
MAX_ACCESSIBLE_COUNT=50
ERROR_SCORE=-999999

grid=[-1]*HEIGHT*WIDTH
heads=[-1]*4
time_at_start=time.time()

def to_at(x, y):
    return x + (y * WIDTH)

def to_xy(at):
    return ((at % WIDTH), int(at / WIDTH))

def set_cell(at, p, on_grid):
    on_grid[at]=p

def get_cell(at, from_grid):
    return from_grid[at]

def get_cell_at(at, from_grid):
    return from_grid[at]

# copies grid as if player p goes in direction
def branch_grid(from_grid, from_heads, p, direction):
    new_p_head = from_heads[p] + direction
    new_grid =from_grid[0:new_p_head] + [p] + from_grid[new_p_head+1:]
    new_heads=from_heads[0:p] + [new_p_head] + from_heads[p+1:]
    return (new_grid, new_heads)


def get_cell_in_direction(at, direction, from_grid):
    return from_grid[at + direction]

def is_direction_valid(at, direction):
    target = at + direction
    if not (0 <= target < HEIGHT*WIDTH):
        return False

    (x,y) = to_xy(at)
    (tx,ty) = to_xy(target)

    return 0 <= tx < WIDTH and 0 <= ty < HEIGHT and ( tx == x or ty == y )

def is_free(at, from_grid):
    return 0 <= at < WIDTH*HEIGHT and get_cell_at(at, from_grid) == -1

def kill(from_grid, player_to_kill):
    return [c if c != player_to_kill else -1 for c in from_grid]

def elapsed_time_ratio():
    current_time = time.time()
    elapsed = current_time - time_at_start
    return elapsed / 0.1 # max time = 100ms

def debug(log, level=LOG_DEBUG):
    if level >= LOG_THRESHOLD:
        print(log, file=sys.stderr, flush=True)

def print_grid(from_grid, from_heads):
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

def choose(p, from_grid, from_heads) -> int:
    valid_moves = get_valid_moves(from_grid, from_heads, P)
    debug(f"Valid moves: { ', '.join([direction_str(d) for d in valid_moves]) }", LOG_DEBUG)

    moves_with_scores : list[tuple[int, int]] = []

    for move in valid_moves:
        score = 0

        for player in range(NB_PLAYERS):
            if player != p: # désactiver l'évaluation pour les autres joueurs
                continue
            coeff = 1 if player == p else -1
            (_, score_for_player) = evaluate_for_player_after_move(
                from_grid,
                from_heads,
                player,
                move,
                coeff,
                DEPTH
            )

            debug(f"Score for player {player} if going {direction_str(move)} : {score_for_player}", LOG_INFO)

            score += score_for_player

        debug(f"Score if going {direction_str(move)} : {score}", LOG_INFO)
        moves_with_scores += [ (move, score) ]

    if not bool(moves_with_scores):
        (max_move,max_score) = [0, ERROR_SCORE]
    else:
        (max_move, max_score) = max(moves_with_scores, key = itemgetter(1))

    debug(f"Best choice: {direction_str(max_move)} ({max_score})", LOG_INFO)

    return max_move

def get_valid_moves(from_grid, from_heads, p) -> list[int]:
    p_at=from_heads[p]

    valid_moves = []
    if is_direction_valid(p_at, D_LEFT) and is_free(p_at + D_LEFT, from_grid):
        valid_moves += [D_LEFT]

    if is_direction_valid(p_at, D_UP) and is_free(p_at + D_UP, from_grid):
        valid_moves += [D_UP]

    if is_direction_valid(p_at, D_RIGHT) and is_free(p_at + D_RIGHT, from_grid):
        valid_moves += [D_RIGHT]

    if is_direction_valid(p_at, D_DOWN) and is_free(p_at + D_DOWN, from_grid):
        valid_moves += [D_DOWN]

    return valid_moves if len(valid_moves) > 0 else [0]

def insert_sorted_desc_from_end(input_list, element, comparison_key_extractor):
    element_key = comparison_key_extractor(element)
    index = len(input_list) -1

    while index >= 0 and element_key > comparison_key_extractor(input_list[index]):
        index -= 1

    # index = -1 or input[index] >= element_key
    input_list.insert(index+1, element)

def minmax_iterative(from_grid, from_heads, depth=0) -> int :

    leafs = []
    remaining : list[tuple[int, int, list[int], list[int]]] = [(
        0, # turn which is used to sort nodes in list
        P, # player of the turn
        from_grid, # state of the grid during the turn,
        from_heads # heads of players during the turn
    )]

    continue_diving = True

    while (continue_diving) :
        (turn, turn_player, turn_grid, turn_heads) = remaining.pop()

        moves = get_valid_moves(turn_grid, turn_heads, turn_player)
        for move in moves:
            (move_grid, move_heads) = branch_grid(turn_grid, turn_heads, turn_player, move)
            insert_sorted_desc_from_end(
                remaining,
                (
                    turn+1,
                    (turn_player+1) % NB_PLAYERS,
                    move_grid,
                    move_heads
                ),
                itemgetter(0)
            )

        continue_diving = bool(remaining) and (elapsed_time_ratio() > 0.5 or turn_player != P)





def evaluate_for_player_after_move(from_grid, from_heads, p, move, coeff=1, depth=0) -> tuple[int, int] :

    time_ratio=elapsed_time_ratio()
    if time_ratio > MAX_TIME_RATIO:
        debug(f"No time left ({time_ratio*100:.2f}%)", LOG_ERROR)
        return (0, 0)
    else:
        debug(f"We still have time ({time_ratio*100:.2f}%)", LOG_DEBUG)

    p_at=from_heads[p]

    (grid_after_move, heads_after_moves)=branch_grid(from_grid, from_heads, p, move)

    debug(f"{' '*(DEPTH-depth)}Evaluating move {direction_str(move)} (={p_at+move})", LOG_DEBUG)
    score_for_move=evaluate_for_player(grid_after_move, heads_after_moves, p, coeff, depth)

    debug(f"{' '*(DEPTH-depth)}Score at move {direction_str(move)} : {score_for_move}, depth={depth}", LOG_INFO)

    if depth > 0:
        valid_moves=get_valid_moves(grid_after_move, heads_after_moves, p)

        moves_with_scores : list[tuple[int, int]] = []

        for next_move in valid_moves:
            if move == 0:
                continue

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

        if bool(moves_with_scores):
            score_for_move += max(moves_with_scores, key = itemgetter(1))[1]
        else:
            score_for_move = ERROR_SCORE

    return (move, score_for_move)

def evaluate_for_player(from_grid, from_heads, p, coeff=1, depth=0) -> int :
    valid_moves=get_valid_moves(from_grid, from_heads, p)

    # prendre en compte la mort 0 = mort
    # mais toute partie fini forcément par mort
    # pour mitiger score = time to death
    # donc mort = 0
    # maximiser sa TTD et diminuer celle des autres
    # des fois, tuer un enemi libère de la place pour un autre
    # appliquer exponentielle ou logarithme

    score = 0
    for move in valid_moves:
        score += count_accessible(from_grid, from_heads[p] + move)

    nb_alive = reduce(lambda sum, head : sum + 1 if head > -1 else sum, from_heads, 0)

    return int(score * coeff / nb_alive) if nb_alive > 0 else 0

def count_accessible(source_grid, origin) -> int :
    counting_grid = source_grid.copy()

    remaining=[origin]
    count=0

    while bool(remaining) and count < MAX_ACCESSIBLE_COUNT: # == is not empty
        current = remaining.pop()

        try:
            if counting_grid[current] == -1:
                count += 1
                counting_grid[current] = 9
                if is_direction_valid(current, D_LEFT):
                    remaining.append(current+D_LEFT)

                if is_direction_valid(current, D_UP):
                    remaining.append(current+D_UP)

                if is_direction_valid(current, D_RIGHT):
                    remaining.append(current+D_RIGHT)

                if is_direction_valid(current, D_DOWN):
                    remaining.append(current+D_DOWN)
        except IndexError :
            debug(f"Index invalid lors du compte: origin={origin} current={current}", LOG_ERROR)
            raise

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
    NB_PLAYERS=n
    P=p
    debug(f"I am p{p}")
    heads=[-1]*NB_PLAYERS
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
            print_grid(grid, heads)
        else:
            at1=to_at(x1, y1)
            set_cell(at1, i, grid)
            heads[i]=at1

            debug(f"p{i} {x1},{y1}={i} (grid = {get_cell(at1, grid)})")

    #print_grid()

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # A single line with UP, DOWN, LEFT or RIGHT
    time_at_start = time_before = time.time()
    direction = choose(p, grid, heads)
    time_after = time.time()

    debug(f"Going {direction_str(direction)} (time: {((time_after - time_before) * 1000):.3f} ms)", LOG_WARN)
    #print_grid(branch_grid(grid, heads, P, direction))



    print_direction(direction)
