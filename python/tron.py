import copy
import sys
import math
from operator import itemgetter
import time
from functools import reduce
from xxlimited_35 import Null

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARN = 2
LOG_ERROR = 3

LOG_THRESHOLD = LOG_INFO

HEIGHT = 20
WIDTH = 30
MAX_CELL = HEIGHT * WIDTH

D_UP = -WIDTH
D_DOWN = +WIDTH
D_LEFT = -1
D_RIGHT = +1

NB_PLAYERS = -1
P = -1

# config
DEPTH = 10
MAX_TIME_RATIO = 0.95
MAX_ACCESSIBLE_COUNT = 50
ERROR_SCORE = -999999

# à convertir en class Timer
def elapsed_time_ratio():
    current_time = time.time()
    elapsed = current_time - time_at_start
    return elapsed / 0.1  # max time = 100ms


def debug(log, level=LOG_DEBUG):
    if level >= LOG_THRESHOLD:
        print(log, file=sys.stderr, flush=True)

def xy_to_cell(x, y):
    return x + (y * WIDTH)

def cell_to_xy(cell):
    return (cell % WIDTH), int(cell / WIDTH)

class Timer:
    start: float

    def __init__(self):
        self.start = time.time()

    def elapsed_time_ratio(self):
        return self.elapsed_time() / 0.1  # max time = 100ms

    def elapsed_time(self):
        current_time = time.time()
        return current_time - self.start

    def reset(self):
        self.start = time.time()


timer = Timer()


class State:
    nb_players: int
    grid: list[int]
    heads: list[int]

    def __init__(self, nb_players):
        self.nb_players = nb_players

        self.grid = [-1] * MAX_CELL
        self.heads = [-1] * self.nb_players

    def get_cell(self, cell):
        return self.grid[cell]

    def get_cell_xy(self, x, y):
        return self.grid[xy_to_cell(x, y)]

    def set_cell(self, cell, value):
        self.grid[cell] = value

    def set_cell_xy(self, x, y, value):
        self.grid[xy_to_cell(x, y)] = value

    def get_head(self, player):
        return self.heads[player]

    def set_head(self, player, cell):
        self.heads[player] = cell

    def set_head_xy(self, player, x, y):
        self.heads[player] = xy_to_cell(x, y)

    def is_free(self, cell):
        return self.grid[cell] == -1

    def is_valid_move(self, origin, direction):
        target = origin + direction
        if not (0 <= target < MAX_CELL):
            return False

        (x, y) = cell_to_xy(origin)
        (tx, ty) = cell_to_xy(target)

        return (tx == x or ty == y) and self.is_free(target)

    def get_valid_moves(self, origin) -> list[int]:
        valid_moves = []
        if self.is_valid_move(origin, D_LEFT):
            valid_moves += [D_LEFT]

        if self.is_valid_move(origin, D_UP):
            valid_moves += [D_UP]

        if self.is_valid_move(origin, D_RIGHT):
            valid_moves += [D_RIGHT]

        if self.is_valid_move(origin, D_DOWN):
            valid_moves += [D_DOWN]

        return valid_moves if len(valid_moves) > 0 else []

    def get_valid_adjacent(self, origin):
        return [origin + move for move in self.get_valid_moves(origin)]

    def get_nb_alive(self):
        return reduce(lambda nb_alive, head: nb_alive + 1 if head > -1 else nb_alive, self.heads, 0)


    def print(self, log_level=LOG_DEBUG):
        header = "_| " + " ".join([str(i % 10) for i in range(WIDTH)])
        debug(header, log_level)
        for y in range(HEIGHT):
            line = f"{y % 10}|"
            for x in range(WIDTH):
                cell = xy_to_cell(x, y)
                value = self.get_cell(cell)
                cell_str = (
                        ('[' if 0 <= value < self.nb_players and self.heads[value] == cell else ' ')
                        +
                        (str(value) if value >= 0 else '.')
                )
                line += cell_str
            debug(line, log_level)

    def with_player_move(self, player, direction):
        new = State(self.nb_players)

        new_player_head = self.get_head(player) + direction
        new.grid = self.grid[0:new_player_head] + [player] + self.grid[new_player_head + 1:]
        new.heads = self.heads[0:player] + [new_player_head] + self.heads[player + 1:]
        return new

    def kill(self, player_to_kill):
        new = State(self.nb_players)
        new.grid = [cell if cell != player_to_kill else -1 for cell in self.grid]
        new.heads = self.heads.copy()
        new.heads[player_to_kill] = -1
        return new

    def copy(self):
        new = State(self.nb_players)
        new.grid = self.grid.copy()
        new.heads = self.heads.copy()
        return new

def choose(p, state: State) -> int:
    valid_moves = state.get_valid_moves(P)
    debug(f"Valid moves: {', '.join([direction_str(d) for d in valid_moves])}", LOG_DEBUG)

    moves_with_scores: list[tuple[int, int]] = []

    for move in valid_moves:
        score = 0

        for player in range(NB_PLAYERS):
            if player != p:  # désactiver l'évaluation pour les autres joueurs
                continue
            coeff = 1 if player == p else -1
            (_, score_for_player) = evaluate_for_player_after_move(
                state,
                player,
                move,
                coeff,
                DEPTH
            )

            debug(f"Score for player {player} if going {direction_str(move)} : {score_for_player}", LOG_INFO)

            score += score_for_player

        debug(f"Score if going {direction_str(move)} : {score}", LOG_INFO)
        moves_with_scores += [(move, score)]

    if not bool(moves_with_scores):
        (max_move, max_score) = [0, ERROR_SCORE]
    else:
        (max_move, max_score) = max(moves_with_scores, key=itemgetter(1))

    debug(f"Best choice: {direction_str(max_move)} ({max_score})", LOG_INFO)

    return max_move

def insert_sorted_desc_from_end(input_list, element, comparison_key_extractor):
    element_key = comparison_key_extractor(element)
    index = len(input_list) - 1

    while index >= 0 and element_key > comparison_key_extractor(input_list[index]):
        index -= 1

    # index = -1 or input[index] >= element_key
    input_list.insert(index + 1, element)


def minmax_iterative(state, depth=0) -> int:
    leafs = []
    remaining: list[tuple[int, int, State]] = [(
        0,  # turn which is used to sort nodes in list
        P,  # player of the turn
        state  # state during the turn,
    )]

    continue_diving = True

    while continue_diving:
        (turn, turn_player, turn_state) = remaining.pop()

        moves = turn_state.get_valid_moves(state.get_head(turn_player))
        for move in moves:
            (move_grid, move_heads) = state.with_player_move(turn_player, move)
            insert_sorted_desc_from_end(
                remaining,
                (
                    turn + 1,
                    (turn_player + 1) % NB_PLAYERS,
                    move_grid,
                    move_heads
                ),
                itemgetter(0)
            )

        continue_diving = bool(remaining) and (elapsed_time_ratio() > 0.5 or turn_player != P)


def evaluate_for_player_after_move(state, player, move, coeff=1, depth=0) -> tuple[int, int]:
    time_ratio = elapsed_time_ratio()
    if time_ratio > MAX_TIME_RATIO:
        debug(f"No time left ({time_ratio * 100:.2f}%)", LOG_ERROR)
        return 0, 0
    else:
        debug(f"We still have time ({time_ratio * 100:.2f}%)", LOG_DEBUG)

    player_head = state.get_head(player)

    state_after_move = state.with_player_move(player, move)

    debug(f"{' ' * (DEPTH - depth)}Evaluating move {direction_str(move)} (={player_head + move})", LOG_DEBUG)
    score_for_move = evaluate_for_player(state_after_move, player, coeff, depth)

    debug(f"{' ' * (DEPTH - depth)}Score at move {direction_str(move)} : {score_for_move}, depth={depth}", LOG_DEBUG)

    if depth > 0:
        valid_moves = state_after_move.get_valid_moves(state_after_move.get_head(player))

        moves_with_scores: list[tuple[int, int]] = []

        for next_move in valid_moves:
            if move == 0:
                continue

            moves_with_scores += [
                evaluate_for_player_after_move(
                    state_after_move,
                    player,
                    next_move,
                    coeff,
                    depth - 1
                )
            ]

        if bool(moves_with_scores):
            score_for_move += max(moves_with_scores, key=itemgetter(1))[1]
        else:
            score_for_move = ERROR_SCORE

    return move, score_for_move


def evaluate_for_player(state, player, coeff=1, depth=0) -> int:
    # prendre en compte la mort 0 = mort
    # mais toute partie fini forcément par mort
    # pour mitiger score = time to death
    # donc mort = 0
    # maximiser sa TTD et diminuer celle des autres
    # des fois, tuer un enemi libère de la place pour un autre
    # appliquer exponentielle ou logarithme

    score = count_accessible(state, state.get_head(player))

    nb_alive = state.get_nb_alive()

    return int(score * coeff / nb_alive) if nb_alive > 0 else 0


def count_accessible(state: State, origin) -> int:
    counting_state = state.copy()
    # counting_state.print(LOG_INFO)

    remaining = [origin]
    count = 0
    while bool(remaining) and count < MAX_ACCESSIBLE_COUNT:  # == is not empty
        current = remaining.pop()
        try:
            if counting_state.is_free(current):
                count += 1
                counting_state.set_cell(current, 9)
                for adjacent in counting_state.get_valid_adjacent(current):
                    remaining.append(adjacent)
        except IndexError:
            debug(f"IndexError: origin={origin} current={current}", LOG_ERROR)
            counting_state.print(LOG_INFO)
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

def game_loop():

    state = None

    while True:
        # n: total number of players (2 to 4).
        # p: your player number (0 to 3).
        NB_PLAYERS, PLAYER = [int(i) for i in input().split()]
        debug(f"I am p{PLAYER}")

        if state is None:
            state = State(NB_PLAYERS)

        for player in range(NB_PLAYERS):
            # x0: starting X coordinate of lightcycle (or -1)
            # y0: starting Y coordinate of lightcycle (or -1)
            # x1: starting X coordinate of lightcycle (can be the same as X0 if you play before this player)
            # y1: starting Y coordinate of lightcycle (can be the same as Y0 if you play before this player)
            x0, y0, x1, y1 = [int(j) for j in input().split()]

            if x0 == -1:
                debug(f"Killing p{player}")
                state.kill(player)
                state.print()
            else:
                cell = xy_to_cell(x1, y1)
                state.set_cell(cell, player)
                state.set_head(player, cell)


        timer.reset()
        state.print(LOG_INFO)
        direction = choose(PLAYER, state)

        debug(f"Going {direction_str(direction)} (time: {((timer.elapsed_time()) * 1000):.3f} ms)", LOG_WARN)

        print_direction(direction)


game_loop()