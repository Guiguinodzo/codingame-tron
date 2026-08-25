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

D_UP = -WIDTH
D_DOWN = +WIDTH
D_LEFT = -1
D_RIGHT = +1

# Performance ratio : 1/(50% quartile of benchmark in 1/1000 of ms)
CODINGAME_SCORE = 1 / 250
H0ST_SCORE = 1 / 190

HOST_MALUS = CODINGAME_SCORE / H0ST_SCORE


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


def group_id_as_code(group_id):
    return chr(ord('A') + (group_id // 26)) + chr(ord('A') + (group_id % 26))


def paint(cell, color=None, text=None, text_color=None, group_id=None):
    if not PAINT_ENABLED or (color is None and text is None):
        return
    x, y = cell_to_xy(cell)
    command = f"#PAINT([{x},{y}]"
    if color is not None:
        command += f",color={color}"
    if text is not None:
        command += f",text=\"{text}\""
    if text_color is not None:
        command += f",text_color={text_color}"
    if group_id is not None:
        command += f",group={group_id}"
    command += ")"
    print(command, file=sys.stderr)


class Timer:
    _start: float
    _steps_duration: dict[str, float]
    _steps_start: dict[str, float]

    def __init__(self):
        self._start = time.time()
        self._steps_duration = {}
        self._steps_start = {}

    def elapsed_time_ratio(self):
        return self.elapsed_time() / MAX_TIME  # max time = 100ms

    def elapsed_time(self) -> float:
        current_time = time.time()
        return current_time - self._start

    def adjusted_elapsed_time_ratio(self):
        return self.adjusted_elapsed_time() / MAX_TIME  # max time = 100ms

    def adjusted_elapsed_time(self):
        return self.elapsed_time() / HOST_MALUS

    def reset(self):
        self._start = time.time()

    def start_step(self, step):
        self._steps_start[step] = time.time()

    def stop_step(self, step) -> float:
        duration = time.time() - self._steps_start[step]
        self._steps_duration[step] = duration
        return duration

    def print_step(self, step, log_level=LOG_DEBUG):
        duration = self._steps_duration[step]

        if PRINT_ADJUSTED:
            debug(
                f"Duration for {step} : {duration * 1000:.2f} ms - Adjusted : {(duration / HOST_MALUS) * 1000:.2f} ms",
                log_level)
        else:
            debug(f'Duration for {step} : {duration * 1000:.2f} ms', log_level)

    def print_elapsed(self, log_level=LOG_INFO):
        elapsed_time: float = self.elapsed_time()
        ratio: float = elapsed_time / MAX_TIME
        adjusted_elapsed_time: float = elapsed_time / HOST_MALUS
        adjusted_ratio: float = adjusted_elapsed_time / MAX_TIME
        debug(f"Time: {elapsed_time * 1000:.3f} ms ({ratio * 100:.2f}%)", log_level)
        if PRINT_ADJUSTED:
            debug(f"Adjusted time: {adjusted_elapsed_time * 1000:.3f} ms ({adjusted_ratio * 100:.2f}%)", log_level)


timer = Timer()


class State:
    nb_players: int
    grid: list[int]
    heads: list[int]
    last_move: list[int]

    def __init__(self, nb_players):
        self.nb_players = nb_players

        self.grid = [-1] * MAX_CELL
        self.heads = [-1] * self.nb_players
        self.last_move = [0] * self.nb_players

    def get_cell(self, cell: int) -> int:
        return self.grid[cell]

    def get_cell_xy(self, x: int, y: int) -> int:
        return self.grid[xy_to_cell(x, y)]

    def set_cell(self, cell: int, value: int) -> None:
        self.grid[cell] = value

    def set_cell_xy(self, x, y, value) -> None:
        self.grid[xy_to_cell(x, y)] = value

    def get_head(self, player: int) -> int:
        return self.heads[player]

    def set_head(self, player: int, cell: int) -> None:
        previous_head = self.heads[player]
        self.heads[player] = cell
        if previous_head != -1:
            self.last_move[player] = self.heads[player] - previous_head

    def set_head_xy(self, player: int, x: int, y: int) -> None:
        self.set_head(player, xy_to_cell(x, y))

    def get_last_move(self, player: int) -> int:
        return self.last_move[player]

    def is_free(self, cell: int) -> bool:
        return self.grid[cell] == -1

    def count_free_cells(self) -> int:
        return reduce(lambda count, cell : count + 1 if cell == -1 else count, self.grid, 0)

    def is_valid_move(self, origin: int, direction: int) -> bool:
        target = origin + direction
        if not (0 <= target < MAX_CELL):
            return False

        (x, y) = cell_to_xy(origin)
        (tx, ty) = cell_to_xy(target)

        orthogonal_move = (tx == x or ty == y)
        free = self.is_free(target)
        return orthogonal_move and free

    def get_valid_moves_for_player(self, player: int) -> list[int]:
        player_cell = self.get_head(player)
        return self.get_valid_moves_from_cell(player_cell)

    def get_valid_moves_from_cell(self, origin: int) -> list[int]:
        valid_moves = []
        for move in (D_LEFT, D_UP, D_RIGHT, D_DOWN):
            if self.is_valid_move(origin, move):
                valid_moves.append(move)

        return valid_moves

    def get_valid_adjacent(self, origin: int) -> list[int]:
        return [origin + move for move in self.get_valid_moves_from_cell(origin)]

    def get_nb_alive(self) -> int:
        return reduce(lambda nb_alive, head: nb_alive + 1 if head > -1 else nb_alive, self.heads, 0)

    def get_alive_players(self) -> list[int]:
        return [player for (player, head) in enumerate(self.heads) if head > -1]

    def is_player_alive(self, player: int) -> bool:
        return self.heads[player] > -1

    def get_winner(self) -> int:
        alive_players = self.get_alive_players()
        return alive_players[0] if len(alive_players) == 1 else -1

    def next_player(self, current_player: int) -> int:
        next_player = (current_player + 1) % self.nb_players
        while not self.is_player_alive(next_player) and next_player != current_player:
            next_player = (next_player + 1) % self.nb_players

        if next_player == current_player:
            raise Exception(f"Player {current_player} wins!")

        return next_player

    def print(self, log_level: int = LOG_DEBUG) -> None:
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

    def with_player_move(self, player: int, direction: int):
        new = State(self.nb_players)

        new_player_head = self.get_head(player) + direction
        new.grid = self.grid[0:new_player_head] + [player] + self.grid[new_player_head + 1:]
        new.heads = self.heads[0:player] + [new_player_head] + self.heads[player + 1:]
        new.last_move = self.last_move[:]
        new.last_move[player] = direction
        return new

    def kill(self, player_to_kill: int):
        new = State(self.nb_players)
        new.grid = [cell if cell != player_to_kill else -1 for cell in self.grid]
        new.heads = self.heads.copy()
        new.heads[player_to_kill] = -1
        new.last_move = self.last_move[:]
        return new

    def copy(self):
        new = State(self.nb_players)
        new.grid = self.grid[:]
        new.heads = self.heads[:]
        new.last_move = self.last_move[:]
        return new


class VoronoiBorder:

    def __init__(self, cell,
                 top: int | None = None,
                 left: int | None = None,
                 bottom: int | None = None,
                 right: int | None = None):
        self.cell = cell
        self.top_player = top
        self.left_player = left
        self.bottom_player = bottom
        self.right_player = right

    def set(self, direction: int, player: int):
        if direction == D_UP:
            self.top_player = player
        elif direction == D_RIGHT:
            self.right_player = player
        elif direction == D_DOWN:
            self.bottom_player = player
        elif direction == D_LEFT:
            self.left_player = player


class Evaluation:
    """ Computes and stores a complete evaluation of a State """
    _current_player: int
    """ Player for which the State is evaluated, usually the player that moved last in this State"""

    _players_order: list[int]
    """Sorted list of players in order of turn. _played_order[0] is the next player"""

    _paths_by_player: dict[int, list[None | list[int]]]
    """For each player, for each cell, the list of cells to be visited in order for that player to reach that cell"""

    _distances_by_player: dict[int, list[int]]
    """For each player, for each cell, the shortest path's length to that cell"""

    _voronoi: list[int]
    """For each cell, the id of the nearest player"""

    _controlled_by_player: dict[int, list[int]]
    """For each player, the list of cell that player is the nearest to"""

    _borders: dict[int, dict[int, VoronoiBorder]]  # by player by cell
    """For each player, for each cell, the list of cells that :
    - is controlled by that player 
    - and is adjacent to at least one cell controlled by another player"""

    _groups: list[list[int]]
    """For each player, for each cell, the id of the group to which this cell belongs, -1 if none"""
    _groups_ids: list[list[int]]
    """For each player, the list of all its group's ids"""
    _group_size: list[list[int]]

    _voronoi_count_by_player_by_group: list[list[int]]
    """For each player, for each group, the count of cells controlled by that player"""
    _voronoi_adjacent_count_by_player_by_group: list[list[int]]
    """For each player, for each group, the sum of adjacent free cells count of cells controlled by that player"""

    _free_adjacent_count_by_player: list[list[int]]
    """For each player, for each cell, the number of free adjacent cells"""

    def __init__(self, state: State, current_player: int):
        self._state = state
        self._current_player = current_player
        self._distances_by_player = {}
        self._voronoi = []
        self._controlled_by_player = {}
        self._paths_by_player = {}
        self._borders = {}
        self._players_order = [(current_player + i) % state.nb_players for i in range(1, state.nb_players + 1)]
        self._groups = [[-1] * MAX_CELL] * state.nb_players
        self._groups_ids = [[]] * state.nb_players
        self._voronoi_count_by_player_by_group = [[]] * state.nb_players
        self._voronoi_adjacent_count_by_player_by_group = [[]] * state.nb_players
        self._free_adjacent_count_by_player = [[0]*MAX_CELL] * state.nb_players

    def get_borders(self, player: int) -> dict[int, VoronoiBorder] | None:
        return self._borders[player] if player in self._borders else None

    def get_distance_for_player(self, player: int, cell: int) -> int:
        return self._distances_by_player[player][cell]

    def get_path(self, player: int, cell: int) -> list[int] | None:
        return self._paths_by_player[player][cell]

    def compute_all(self, evaluation_id: str = "default"):
        step_compute_all = f"evaluation.compute_all_{evaluation_id}"
        timer.start_step(step_compute_all)

        self._compute_distance_for_all()
        self._compute_voronoi()

        timer.stop_step(step_compute_all)
        timer.print_step(step_compute_all)

    def _compute_distance_for_all(self):
        for player in self._state.get_alive_players():
            self._compute_distance_and_path_for_player(player)

    def _compute_distance_and_path_for_player(self, player: int):
        step = f"evaluation.compute_distance_and_path_for_{player}"
        timer.start_step(step)

        paths: list[None | list[int]] = [None] * MAX_CELL
        distances = [MAX_CELL] * MAX_CELL

        groups_enabled = self._current_player == player

        # TODO : grouper les cellules
        # - pour une cellule
        #   - verifier si voisine visited
        #       - si 1 : groupe de cette cellule
        #       - si 2+ : groupe cellule 1 + ajouter association de tous les groupes
        #       - si 0 : nouveau groupe
        # - structure donnée : groups = list[int] = -1 * MAX_CELL
        #       - groups[id_group]=id_group
        #       - groups[3]=3 => le group 3 existe (et commence par la cellule 3)
        #       - groups[15]=5 => le group 15 doit être fusionné avec groupe 5
        #       - groups[X]=-1 => pas un group
        # - écrire n° group de chaque case à la fin
        # - dans voronoi => faire aussi voronoi/group

        origin = self._state.get_head(player)
        paths[origin] = [origin]
        remaining = deque()
        for adjacent in self._state.get_valid_adjacent(origin):
            if self._state.is_free(adjacent):
                remaining.appendleft((adjacent, [origin], 1))

        self._groups[player] = [-1] * MAX_CELL
        self._group_size = [[0]*MAX_CELL] * self._state.nb_players

        visited = [False] * MAX_CELL
        while remaining:
            current_cell, path, current_distance = remaining.pop()
            if visited[current_cell]:
                continue
            visited[current_cell] = True
            distances[current_cell] = current_distance
            paths[current_cell] = path + [current_cell]
            adjacent_groups = [-1] * 4 if groups_enabled else []
            nb_adjacent_in_groups = 0
            valid_adjacent_cells = self._state.get_valid_adjacent(current_cell)
            self._free_adjacent_count_by_player[player][current_cell] = len(valid_adjacent_cells)
            for adjacent in valid_adjacent_cells:
                if not visited[adjacent]:
                    remaining.appendleft((adjacent, paths[current_cell], current_distance + 1))
                elif groups_enabled and visited[adjacent] and self._groups[player][adjacent] != -1:
                    adjacent_groups[nb_adjacent_in_groups] = self._groups[player][adjacent]
                    nb_adjacent_in_groups += 1

            if groups_enabled:
                if nb_adjacent_in_groups == 0:
                    self._groups[player][current_cell] = current_cell
                elif nb_adjacent_in_groups == 1:
                    self._groups[player][current_cell] = adjacent_groups[0]
                else:
                    lowest_group_id = min(adjacent_groups, key=lambda x: x if x != -1 else MAX_CELL)
                    self._groups[player][current_cell] = lowest_group_id
                    for group_to_merge_idx in range(0, nb_adjacent_in_groups):
                        group_id_of_adjacent = adjacent_groups[group_to_merge_idx]
                        if group_id_of_adjacent == lowest_group_id:
                            continue
                        self._groups[player][group_id_of_adjacent] = lowest_group_id
        self._paths_by_player[player] = paths
        self._distances_by_player[player] = distances

        if groups_enabled:
            timer.start_step("group_resolution")
            for cell in range(MAX_CELL):
                if self._groups[player][cell] == -1:
                    continue
                elif self._groups[player][cell] == cell:
                    self._groups_ids[player].append(cell)
                    self._group_size[player][cell] += 1
                    continue

                resolved_group_id = self._groups[player][cell]
                while self._groups[player][resolved_group_id] != resolved_group_id:
                    new_resolved_group_id = self._groups[player][resolved_group_id]
                    resolved_group_id = new_resolved_group_id
                self._groups[player][cell] = resolved_group_id
                self._group_size[player][resolved_group_id] += 1
            timer.stop_step("group_resolution")
            timer.print_step("group_resolution")
            debug(f"Group resolution complete, {len(self._groups_ids[player])} group(s) detected")

        timer.stop_step(step)
        timer.print_step(step)

    def _compute_voronoi(self):
        step = "evaluation.compute_voronoi"
        timer.start_step(step)

        self._voronoi = [-1] * MAX_CELL
        self._controlled_by_player = {}
        for player in self._state.get_alive_players():
            self._controlled_by_player[player] = []

        for player in range(self._state.nb_players):
            self._voronoi_count_by_player_by_group[player] = [0] * len(self._groups_ids[player])
            self._voronoi_adjacent_count_by_player_by_group[player] = [0] * len(self._groups_ids[player])

        for cell in range(MAX_CELL):

            controlling_player = min(self._distances_by_player.keys(),
                                     key=lambda p: self._distances_by_player[p][cell] * 10 + self._players_order[p]
                                     # + (1 if self._current_player != player else 0) # TODO +1 aux adversaire pour compenser depth = 1 => à améliorer
                                     )
            if self._distances_by_player[controlling_player][cell] == MAX_CELL:
                continue
            self._voronoi[cell] = controlling_player
            self._controlled_by_player[controlling_player].append(cell)

            if self._current_player == controlling_player:  # only for current player for which groups are enabled
                cell_group_id = self._groups[controlling_player][cell]
                group_index = self._groups_ids[controlling_player].index(cell_group_id)
                self._voronoi_count_by_player_by_group[controlling_player][group_index] += 1
                self._voronoi_adjacent_count_by_player_by_group[controlling_player][group_index] += self._free_adjacent_count_by_player[controlling_player][cell]

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
        player_text_colors = ['#000000', '#000000', '#000000', '#000000']

        for cell in range(MAX_CELL):
            player = self._voronoi[cell]
            if player < 0:
                continue
            is_border = player in self._borders and cell in self._borders[player]
            color = player_border_colors[player] if is_border else player_colors[player]
            text = group_id_as_code(self._groups[self._current_player][cell]) if self._groups[self._current_player][
                                                                                     cell] != -1 else None
            text_color = player_text_colors[self._current_player]
            paint(cell, color=color, text=text, text_color=text_color, group_id=group_id)

    def score(self, player: int) -> list[float |int]:
        # voronoi_score = reduce(
        #     lambda score, voronoi_cell: score + 1,
        #     # lambda score, voronoi_cell : score + MAX_CELL / self.get_distance_for_player(player, voronoi_cell),
        #     self._controlled_by_player[player],
        #     0.0
        # )

        voronoi_count_by_group = self._voronoi_count_by_player_by_group[player]
        voronoi_score = max(voronoi_count_by_group) if len(voronoi_count_by_group) > 0 else 0

        voronoi_adjacent_count_by_group = self._voronoi_adjacent_count_by_player_by_group[player]
        voronoi_adjacent_count_score = max(voronoi_adjacent_count_by_group) if len(voronoi_adjacent_count_by_group) > 0 else 0

        min_border_distance = MAX_CELL
        borders = self.get_borders(player)
        if borders:
            for (border_cell, _) in borders.items():
                distance = self.get_distance_for_player(player, border_cell)
                if distance < min_border_distance:
                    min_border_distance = distance

        return [voronoi_score, voronoi_adjacent_count_score, -1 * min_border_distance]

    def is_better(self, player, other) -> bool:
        other_score = other.score(self._current_player)

        return self.score(player) > other_score


def choose_based_on_evaluation(me: int, state: State, depth=0, move_before='') -> tuple[int, Evaluation | None]:
    moves = state.get_valid_moves_for_player(me)

    best_move = D_UP
    best_evaluation = None
    for move in moves:
        state_with_player_move = state.with_player_move(me, move)

        for player_delta in range(1, state_with_player_move.nb_players):
            player = (me + player_delta) % state_with_player_move.nb_players
            if not state_with_player_move.is_player_alive(player):
                continue
            player_last_move = state_with_player_move.last_move[player]
            debug(f'player {player} last move was {direction_str(player_last_move)}')
            valid_moves_for_player = state_with_player_move.get_valid_moves_for_player(player)
            if player_last_move in valid_moves_for_player:
                debug(f'assume {player} keeps going {direction_str(player_last_move)}')
                state_with_player_move = state_with_player_move.with_player_move(player, player_last_move)
            elif valid_moves_for_player:
                debug(f'default move for {player} is {direction_str(valid_moves_for_player[0])}')
                state_with_player_move = state_with_player_move.with_player_move(player, valid_moves_for_player[0])
            else:
                debug(f'assume {player} dies')
                state_with_player_move = state_with_player_move.kill(player)

        move_id = f'{move_before}{direction_str(move)}'
        timer.start_step(move_id)
        if depth == 0:
            if TIME_CUTOFF and timer.elapsed_time_ratio() > 0.85:
                debug(f'Time almost out: {timer.elapsed_time_ratio() * 100:.2f} % '
                      f'({timer.elapsed_time() * 1000:.2f} ms)', LOG_ERROR)
                break
            evaluation = Evaluation(state_with_player_move, me)
            evaluation.compute_all(move_id)
            evaluation.paint(move_id)
        else:
            _, evaluation = choose_based_on_evaluation(me, state_with_player_move, depth - 1,
                                                                               f'{move_id}_')

        if not best_evaluation or (evaluation and evaluation.is_better(me, best_evaluation)):
            best_move, best_evaluation = move, evaluation
        timer.stop_step(move_id)
        timer.print_step(move_id)

    return best_move, best_evaluation


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

        free_cells = state.count_free_cells()
        debug(f"Free cell count: {free_cells}") # 350 > depth 2 OK

        depth = 1 if free_cells > 350 else 2

        direction, _ = choose_based_on_evaluation(me, state, depth)

        moves_for_player = state.get_valid_moves_for_player(me)

        if moves_for_player and direction not in moves_for_player:
            debug(f"Move {direction_str(direction)} is not valid, picking {direction_str(moves_for_player[0])} out of "
                  f"{[direction_str(m) for m in moves_for_player]}", LOG_WARN)
            direction = moves_for_player[0]

        timer.print_elapsed()
        debug(f"Going {direction_str(direction)}\n", LOG_INFO)

        # le simulateur va attendre ce log
        debug("END_OF_LOGS", LOG_INFO)

        print_direction(direction)


# config
LOG_THRESHOLD = LOG_INFO
MAX_TIME = 0.1

hostname = socket.gethostname()
debug(
    f"Sys: {os.name} Platform: {platform.system()} Release: {platform.release()} Python: {platform.python_version()} Hostname: {hostname}",
    LOG_INFO)

on_codingame = 'codemachine' in hostname

if not on_codingame:
    debug("Not on codingame: set log lvl to DEBUG", LOG_INFO)
    LOG_THRESHOLD = LOG_DEBUG
    PAINT_ENABLED = True
    PRINT_ADJUSTED = True
    TIME_CUTOFF = False
    DEPTH=2
else:
    debug("On codingame, log lvl = INFO", LOG_INFO)
    PRINT_ADJUSTED = False
    PAINT_ENABLED = False
    TIME_CUTOFF = True
    DEPTH=1

game_loop()
