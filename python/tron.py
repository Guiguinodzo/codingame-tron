import os
import platform
import socket
import sys
import time
from collections import deque
from functools import reduce

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARN = 2
LOG_ERROR = 3

HEIGHT = 20
WIDTH = 30
MAX_CELL = HEIGHT * WIDTH

MAX_SCORE = WIDTH * HEIGHT * 1001 + 1

D_UP = -WIDTH
D_DOWN = +WIDTH
D_LEFT = -1
D_RIGHT = +1

# Performance ratio : 1/(50% quartile of benchmark in 1/1000 of ms)
CODINGAME_SCORE=1/250
H0ST_SCORE=1/190

HOST_MALUS=CODINGAME_SCORE/H0ST_SCORE

PAINT_ENABLED=False

def print_direction(direction):
    print(direction_str(direction))

def direction_str(direction):
    return (
        'LEFT' if direction == D_LEFT else
        'UP' if direction == D_UP else
        'RIGHT' if direction == D_RIGHT else
        'DOWN' if direction == D_DOWN else
        'DOWN'
    )

def debug(log, level=LOG_DEBUG):
    if level >= LOG_THRESHOLD:
        print(log, file=sys.stderr, flush=True)

def xy_to_cell(x, y):
    return x + (y * WIDTH)

def cell_to_xy(cell):
    return (cell % WIDTH), int(cell / WIDTH)

def paint(cell, color=None, text=None, group_id=None):
    if not PAINT_ENABLED or (color is None and text is None):
        return
    x, y = cell_to_xy(cell)
    command = f"#PAINT([{x},{y}]"
    if color is not None:
        command += f",color={color}"
    if text is not None:
        command += f",text=\"{text}\""
    if group_id is not None:
        command += f",group={group_id}"
    command += ")"
    print(command, file=sys.stderr)

class Timer:
    _start: float
    _steps_duration: dict[str,float]
    _steps_start: dict[str,float]

    def __init__(self):
        self._start = time.time()
        self._steps_duration = {}
        self._steps_start = {}

    def elapsed_time_ratio(self):
        return self.elapsed_time() / MAX_TIME  # max time = 100ms

    def elapsed_time(self):
        current_time = time.time()
        return current_time - self._start

    def reset(self):
        self._start = time.time()

    def start_step(self, step):
        self._steps_start[step] = time.time()

    def stop_step(self, step) -> float:
        duration = time.time() - self._steps_start[step]
        self._steps_duration[step] = duration
        return duration

    def print_step(self, step, log_level = LOG_DEBUG):
        duration = self._steps_duration[step]
        debug(f'Duration for {step} : {duration*1000:.2f} (adjusted: {(duration/HOST_MALUS)*1000:.2f} ms)', log_level)


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

        orthogonal_move = (tx == x or ty == y)
        free = self.is_free(target)
        return orthogonal_move and free

    def get_valid_moves_for_player(self, player) -> list[int]:
        player_cell = self.get_head(player)
        return self.get_valid_moves_from_cell(player_cell)

    def get_valid_moves_from_cell(self, origin) -> list[int]:
        valid_moves = []
        for move in (D_LEFT, D_UP, D_RIGHT, D_DOWN):
            if self.is_valid_move(origin, move):
                valid_moves.append(move)

        return valid_moves

    def get_valid_adjacent(self, origin):
        return [origin + move for move in self.get_valid_moves_from_cell(origin)]

    def get_nb_alive(self):
        return reduce(lambda nb_alive, head: nb_alive + 1 if head > -1 else nb_alive, self.heads, 0)

    def get_alive_players(self):
        return [player for (player, head) in enumerate(self.heads) if head > -1]

    def is_player_alive(self, player):
        return self.heads[player] > -1

    def get_winner(self) -> int:
        alive_players = self.get_alive_players()
        return alive_players[0] if len(alive_players) == 1 else -1

    def next_player(self, current_player):
        next_player = (current_player + 1) % self.nb_players
        while not self.is_player_alive(next_player) and next_player != current_player:
            next_player = (next_player + 1) % self.nb_players

        if next_player == current_player:
            raise Exception(f"Player {current_player} wins!")

        return next_player


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
        new.grid = self.grid[:]
        new.heads = self.heads[:]
        return new

class VoronoiBorder:

    def __init__(self, cell, top=None, left=None, bottom=None, right=None):
        self.cell = cell
        self.top_player = top
        self.left_player = left
        self.bottom_player = bottom
        self.right_player = right

    def set(self, direction, player):
        if direction == D_UP:
            self.top_player = player
        elif direction == D_RIGHT:
            self.right_player = player
        elif direction == D_DOWN:
            self.bottom_player = player
        elif direction == D_LEFT:
            self.left_player = player

class Evaluation:
    """ Stocke l'ensemble des évaluations faites sur un State """

    _paths_by_player : dict[int, list[None|list[int]]]
    _distances_by_player : dict[int, list[int]]
    _voronoi : list[int]
    _controlled_by_player : dict[int, list[int]]
    _borders : dict[int, dict[int, VoronoiBorder]] # by player by cell

    def __init__(self, state: State, current_player: int):
        self._state = state
        self._current_player = current_player
        self._distances_by_player = {}
        self._voronoi =[]
        self._controlled_by_player = {}
        self._paths_by_player = {}
        self._borders = {}
        self._players_order = [
            player_index - current_player if player_index >= current_player
            else player_index + current_player
            for player_index in range(4)
        ]

    def get_borders(self, player):
        return self._borders[player] if player in self._borders else None

    def get_distance_for_player(self, player, cell):
        return self._distances_by_player[player][cell]

    def get_path(self, player, cell):
        return self._paths_by_player[player][cell]

    def compute_all(self):
        step_compute_all = "evaluation.compute_all"
        timer.start_step(step_compute_all)

        self._compute_distance_for_all()
        self._compute_voronoi()

        timer.stop_step(step_compute_all)
        timer.print_step(step_compute_all)

    def _compute_distance_for_all(self):
        for player in self._state.get_alive_players():
            self._compute_distance_and_path_for_player(player)

    def _compute_distance_and_path_for_player(self, player):
        step = f"evaluation.compute_distance_and_path_for_{player}"
        timer.start_step(step)

        paths : list[None|list[int]] = [None]*MAX_CELL
        distances = [MAX_CELL]*MAX_CELL

        origin = self._state.get_head(player)
        paths[origin] = [origin]
        remaining = deque()
        for adjacent in self._state.get_valid_adjacent(origin):
            if self._state.is_free(adjacent):
                remaining.appendleft((adjacent, [origin], 1))

        visited = [False]*MAX_CELL
        while remaining:
            current_cell, path, current_distance = remaining.pop()
            if visited[current_cell]:
                continue
            visited[current_cell] = True
            distances[current_cell] = current_distance
            paths[current_cell] = path + [current_cell]
            for adjacent in self._state.get_valid_adjacent(current_cell):
                if self._state.is_free(adjacent) and not visited[adjacent]:
                    remaining.appendleft((adjacent, paths[current_cell], current_distance + 1))

        self._paths_by_player[player] = paths
        self._distances_by_player[player] = distances
        timer.stop_step(step)
        timer.print_step(step)

    def _compute_voronoi(self):
        step = "evaluation.compute_voronoi"
        timer.start_step(step)

        self._voronoi = [-1] * MAX_CELL
        self._controlled_by_player = {}
        for player in self._state.get_alive_players():
            self._controlled_by_player[player] = []
        for cell in range(MAX_CELL):
            # TODO: prendre en compte l'ordre des joueurs pour la priorité!
            controlling_player = min(self._distances_by_player.keys(), key=lambda p : self._distances_by_player[p][cell] * 10 + self._players_order[p])
            if self._distances_by_player[controlling_player][cell] == MAX_CELL:
                continue
            self._voronoi[cell] = controlling_player
            self._controlled_by_player[controlling_player].append(cell)

            if self._state.is_valid_move(cell, D_UP):
                top_cell = cell + D_UP
                top_player = self._voronoi[top_cell]
                if top_player != controlling_player and top_player >= 0:
                    self._set_border(controlling_player, cell, top_player, top_cell)
            if self._state.is_valid_move(cell, D_LEFT):
                left_cell = cell + D_LEFT
                left_player = self._voronoi[left_cell]
                if left_player != controlling_player and left_player >= 0:
                    self._set_border(controlling_player, cell, left_player, left_cell)

        timer.stop_step(step)
        timer.print_step(step)

    def _set_border(self, player_a, cell_a, player_b, cell_b):
        border_a = self._borders.setdefault(player_a, {}).setdefault(cell_a, VoronoiBorder(player_a))
        border_a.set(cell_b - cell_a, player_b)

        border_b = self._borders.setdefault(player_b, {}).setdefault(cell_b, VoronoiBorder(player_b))
        border_b.set(cell_a - cell_b, player_b)

    def paint(self, group_id=None):
        player_colors = ['#F52727', '#F5F527', '#27F5F5', '#2727F5']
        player_border_colors = ['#F5278E', '#F58E27', '#27F58E', '#278EF5']
        for cell in range(MAX_CELL):
            player = self._voronoi[cell]
            if player < 0:
                continue
            is_border = player in self._borders and cell in self._borders[player]
            color = player_border_colors[player] if is_border else player_colors[player]
            paint(cell, color, group_id=group_id)

    def evaluate(self, player) -> tuple[int,int]:
        voronoi_size = len(self._controlled_by_player[player])
        min_border_distance = MAX_CELL
        borders = self.get_borders(player)
        if not borders:
            return voronoi_size, MAX_CELL
        for (border_cell, _) in borders.items():
            distance = self.get_distance_for_player(player, border_cell)
            if distance < min_border_distance:
                min_border_distance = distance
        return voronoi_size, min_border_distance


def choose_based_on_evaluation(me: int, turn: int, state: State) -> int:
    moves = state.get_valid_moves_for_player(me)

    best_move = D_UP
    best_voronoi_size, best_min_border_distance = 0, MAX_CELL
    for move in moves:
        state_with_player_move = state.with_player_move(me, move)
        evaluation = Evaluation(state_with_player_move, me)
        evaluation.compute_all()
        evaluation.paint(direction_str(move))
        voronoi_size, min_border_distance = evaluation.evaluate(me)
        if voronoi_size > best_voronoi_size or (voronoi_size == best_voronoi_size and min_border_distance < best_min_border_distance):
            best_voronoi_size, best_min_border_distance, best_move  = voronoi_size, min_border_distance, move

    return best_move

def game_loop():

    state = None
    turn = 0

    while True:
        # n: total number of players (2 to 4).
        # p: your player number (0 to 3).
        nb_players, me = [int(i) for i in input().split()]
        # if turn == 0:
        debug(f"I am p{me}")
        turn += 1

        if state is None:
            state = State(nb_players)

        for player in range(nb_players):
            # x0: starting X coordinate of lightcycle (or -1)
            # y0: starting Y coordinate of lightcycle (or -1)
            # x1: starting X coordinate of lightcycle (can be the same as X0 if you play before this player)
            # y1: starting Y coordinate of lightcycle (can be the same as Y0 if you play before this player)
            x0, y0, x1, y1 = [int(j) for j in input().split()]

            if x0 == -1:
                if state.is_player_alive(player):
                    debug(f"Killing p{player}")
                    state = state.kill(player)
            else:
                cell0 = xy_to_cell(x0, y0)
                cell1 = xy_to_cell(x1, y1)
                state.set_cell(cell0, player)
                state.set_cell(cell1, player)
                state.set_head(player, cell1)


        timer.reset()

        direction = choose_based_on_evaluation(me, turn, state)

        debug(f"Going {direction_str(direction)} (time: {((timer.elapsed_time()) * 1000):.3f} ms = {timer.elapsed_time_ratio() * 100:.2f}%)", LOG_WARN)

        print_direction(direction)

# config
LOG_THRESHOLD = LOG_INFO
MAX_TIME=0.1

hostname = socket.gethostname()
debug(f"Sys: {os.name} Platform: {platform.system()} Release: {platform.release()} Python: {platform.python_version()} Hostname: {hostname}", LOG_INFO)

on_codingame='codemachine' in hostname

if not on_codingame:
    debug("Not on codingame: set log lvl to DEBUG", LOG_INFO)
    LOG_THRESHOLD=LOG_DEBUG
    MAX_TIME=MAX_TIME * HOST_MALUS
    PAINT_ENABLED=True
else:
    debug("On codingame, log lvl = INFO", LOG_INFO)

# config
MAX_DEPTH = 4
MAX_TIME_RATIO = 1
MAX_ACCESSIBLE_COUNT = 50
ERROR_SCORE = -999999
FREE_SPACE_PER_USER_THRESHOLD=100

game_loop()
