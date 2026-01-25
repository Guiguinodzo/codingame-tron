import os
import platform
import socket
import sys
import time
from collections import deque
from functools import reduce
from operator import itemgetter
from typing import Self

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARN = 2
LOG_ERROR = 3

HEIGHT = 20
WIDTH = 30
MAX_CELL = HEIGHT * WIDTH

MAX_SCORE = WIDTH * HEIGHT

D_UP = -WIDTH
D_DOWN = +WIDTH
D_LEFT = -1
D_RIGHT = +1

def debug(log, level=LOG_DEBUG):
    if level >= LOG_THRESHOLD:
        print(log, file=sys.stderr, flush=True)

def xy_to_cell(x, y):
    return x + (y * WIDTH)

def cell_to_xy(cell):
    return (cell % WIDTH), int(cell / WIDTH)

class Timer:
    start: float
    steps: dict[str,float]

    def __init__(self):
        self.start = time.time()
        self.steps = {}

    def elapsed_time_ratio(self):
        return self.elapsed_time() / 0.1  # max time = 100ms

    def elapsed_time(self):
        current_time = time.time()
        return current_time - self.start

    def reset(self):
        self.start = time.time()

    def start_step(self, step):
        self.steps[step] = time.time()

    def stop_step(self, step) -> float:
        return time.time() - self.steps.pop(step)

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

def choose(me: int, state: State) -> int:
    valid_moves = state.get_valid_moves_for_player(me)
    debug(f"Valid moves for p{me}: {', '.join([direction_str(d) for d in valid_moves])}", LOG_INFO)

    moves_with_scores: list[tuple[int, int]] = []

    for move in valid_moves:

        state_with_player_move = state.with_player_move(me, move)

        score = evaluate_for_player(state_with_player_move, me)

        debug(f"Score if going {direction_str(move)} : {score}", LOG_INFO)
        moves_with_scores += [(move, score)]

    if not bool(moves_with_scores):
        (max_move, max_score) = [0, ERROR_SCORE]
    else:
        (max_move, max_score) = max(moves_with_scores, key=itemgetter(1))

    debug(f"Best choice: {direction_str(max_move)} ({max_score})", LOG_INFO)

    return max_move

def choose_minimax_one(me: int, state: State) -> int:

    best_move = 0
    best_score = -MAX_SCORE
    my_possible_moves = state.get_valid_moves_for_player(me)
    debug(f"My possible moves: {[direction_str(move) for move in my_possible_moves]}")
    for move in my_possible_moves:
        debug(f"Evaluating my ({me}) move: {direction_str(move)}")
        state_after_previous_player = state.with_player_move(me, move)

        worst_score = MAX_SCORE
        for turn in range(1, state.nb_players):
            next_player = (me + turn) % state.nb_players
            if not state.is_player_alive(next_player):
                continue
            next_player_moves = state_after_previous_player.get_valid_moves_for_player(next_player)
            debug(f"Player {next_player} possible moves: {[direction_str(move) for move in next_player_moves]}")
            worst_score = MAX_SCORE
            worst_state = None
            for next_player_move in next_player_moves:
                debug(f"Evaluating move of player {next_player}: {direction_str(next_player_move)}")
                state_after_next_player_move = state_after_previous_player.with_player_move(next_player, next_player_move)
                score = evaluate_for_player(state_after_next_player_move, me)
                if score < worst_score:
                    worst_score = score
                    worst_state = state_after_next_player_move
                    debug(f"New worst score for player {next_player}: {worst_score} ({direction_str(next_player_move)})")
            if worst_state is not None:
                state_after_previous_player = worst_state

        if worst_score > best_score:
            best_score = worst_score
            best_move = move
            debug(f"New best score : {best_score} ({direction_str(best_move)})")


    return best_move

def insert_sorted_desc_from_end(input_list, element, comparison_key_extractor):
    element_key = comparison_key_extractor(element)
    index = len(input_list) - 1

    while index >= 0 and element_key > comparison_key_extractor(input_list[index]):
        index -= 1

    # index = -1 or input[index] >= element_key
    input_list.insert(index + 1, element)

class Node:
    state: State
    current_player: int
    move: int
    max: bool
    """ 
    Move that resulted in this node and state (the move is already performed by parent.current_user).\n 
    Original node's move = 0 
    """

    depth: int

    visited: bool
    """ False the first time the node is visited, True afterwards """
    score: int

    parent: Self
    children: list[Self]
    children_index: int

    def __init__(self, me, state: State, current_player: int, move: int, depth: int, parent=None):
        self.state = state
        self.current_player = current_player
        self.move = move
        self.max = current_player == me
        self.depth = depth
        self.visited = False
        self.score = -MAX_SCORE if me == current_player else -MAX_SCORE
        self.parent = parent
        self.children = []
        self.children_index = 0

    def id(self):
        """
            id = [parent_id].<parent.current_player><+ if max, - if min><self.move short name>\n
            ex: "#2+R.3-D.0-L.1-U" means player 2 (me so max) moved Right, then player 3 (min) moved Down,
            then player 0 (min) moved Left and then player 1 (min) moved Up
        """
        if self.parent is None:
            return "#"
        else:
            move_short_name = direction_str(self.move)[0]
            return f"{self.parent.id()}.{self.parent.current_player}{'+' if self.max else '-'}{move_short_name}"

    def is_max(self) -> bool:
        return self.max

    def add_child(self, node: Self):
        self.children.append(node)

    def current_child(self) -> Self:
        return self.children[self.children_index] if self.children_index < len(self.children) else None

    def next_child(self) -> Self:
        self.children_index += 1
        return self.children[self.children_index] if self.children_index < len(self.children) else None

def minimax(state, me, max_depth=600, max_elapsed_time_ratio = 0.0) -> int:

    origin_node = Node(me, state, me, 0, 0)

    alpha = -MAX_SCORE
    """
    on max node: if child.score > alpha then exit without visiting others children\n
    on min node: if child.score < alpha then alpha = child.score 
    """

    beta = MAX_SCORE
    """
    on min node: if child.score < beta then exit without visiting others children\n
    on max node: if child.score > beta then beta = child.score 
    """

    nb_visited = 0
    nb_terminal_visited = 0
    max_depth_reached = 0

    indent="  "

    current_node = origin_node
    while True:
        if current_node is None:
            break

        nb_visited += 1
        if current_node.depth >= max_depth_reached:
            max_depth_reached = current_node.depth

        moves = current_node.state.get_valid_moves_for_player(current_node.current_player)
        debug(f"{indent * current_node.depth}Current node: {current_node.id()} with moves: {[direction_str(move) for move in moves]}")

        depth_limit_reached = (current_node.depth >= max_depth
                               or (0 < max_elapsed_time_ratio < timer.elapsed_time_ratio()))

        is_terminal_node = (
                (not moves and current_node.current_player == me) # my turn and no move = loss
                or (current_node.state.get_winner() == me) # I won
                or (current_node.current_player == me and depth_limit_reached)
            # limit depth by depth or by time
        )

        if is_terminal_node:
            current_node.score = evaluate_for_player(current_node.state, me)
            current_node.visited = True
            current_node = current_node.parent
            nb_terminal_visited += 1

        elif not current_node.visited and moves:
            current_node.visited = True
            current_node.score = -MAX_SCORE if current_node.is_max() else MAX_SCORE
            current_node.children = []

            for move in moves:
                state_after_player_move = current_node.state.with_player_move(current_node.current_player, move)
                # todo : next_player/current_player should be in state
                next_player = state_after_player_move.next_player(current_node.current_player)
                child_node = Node(me, state_after_player_move, next_player, move, current_node.depth + 1)
                child_node.parent = current_node
                current_node.add_child(child_node)

            current_node = current_node.current_child()

        elif not current_node.visited and not moves and current_node.current_player != me:
            current_node.visited = True
            current_node.score = -MAX_SCORE if current_node.is_max() else MAX_SCORE
            current_node.children = []

            state_after_player_death = current_node.state.kill(current_node.current_player)
            next_player = state_after_player_death.next_player(current_node.current_player)
            child_node = Node(me, state_after_player_death, next_player, D_DOWN, current_node.depth + 1)
            child_node.parent = current_node
            current_node.add_child(child_node)

            current_node = child_node

        elif current_node.is_max():
            last_solved_child = current_node.current_child()
            debug(f"{indent * current_node.depth}last_solved_child is None. current: {current_node.id()} index: {current_node.children_index} len(children)={len(current_node.children)}")
            if last_solved_child.score > current_node.score:
                current_node.score = last_solved_child.score
                debug(f"{current_node.id()} Update score: {last_solved_child.id()}.score = {last_solved_child.score} > {current_node.score}")

            if last_solved_child.score >= beta:
                # this node score is already better than the worst score on the above min step, so it's wont be kept
                debug(f"{indent * current_node.depth}{current_node.id()} Beta pruning: {last_solved_child.id()}.score = {last_solved_child.score} < beta = {beta}")
                current_node = current_node.parent
                continue

            if last_solved_child.score > alpha:
                debug(f"{indent * current_node.depth}{current_node.id()} Update alpha: {last_solved_child.id()}.score = {last_solved_child.score} < alpha = {alpha}")
                alpha = last_solved_child.score

            next_child = current_node.next_child()

            if next_child is not None:
                current_node = next_child
            else:
                current_node = current_node.parent

        else: # min
            last_solved_child = current_node.current_child()

            if last_solved_child is None:
                debug(f"{indent * current_node.depth}last_solved_child is None. current: {current_node.id()} index: {current_node.children_index} len(children)={len(current_node.children)}")
            if last_solved_child.score < current_node.score:
                current_node.score = last_solved_child.score
                debug(f"{indent * current_node.depth}{current_node.id()} Update score: {last_solved_child.id()}.score = {last_solved_child.score} < {current_node.score}")

            if last_solved_child.score <= alpha:
                # this node score is already worse than the best score on the above max step, so it's wont be kept
                debug(f"{indent * current_node.depth}{current_node.id()} Alpha pruning: {last_solved_child.id()}.score = {last_solved_child.score} > alpha = {alpha}")
                current_node = current_node.parent
                continue

            if last_solved_child.score < beta:
                debug(f"{indent * current_node.depth}{current_node.id()} Update beta: {last_solved_child.id()}.score = {last_solved_child.score} > beta = {beta}")
                beta = last_solved_child.score

            next_child = current_node.next_child()
            if next_child is not None:
                current_node = next_child
            else:
                current_node = current_node.parent

    debug(f"End of minmax. Nb visited: {nb_visited}, Nb terminal visited: {nb_terminal_visited}, Max depth reached: {max_depth_reached}", LOG_INFO)

    if origin_node.children:
        best_child_node = max(origin_node.children, key=lambda child: child.score)
        debug(f"Best node: {best_child_node.id()} with score: {best_child_node.score} : {direction_str(best_child_node.move)}", LOG_INFO)
        return best_child_node.move
    else:
        debug("No possible moves, going down both figuratively and literally.", LOG_ERROR)
        return D_DOWN

def evaluate_for_player(state, me) -> int:
    # prendre en compte la mort 0 = mort
    # mais toute partie fini forcément par mort
    # pour mitiger score = time to death
    # donc mort = 0
    # maximiser sa TTD et diminuer celle des autres
    # des fois, tuer un enemi libère de la place pour un autre
    # appliquer exponentielle ou logarithme

    if state.get_winner() == me:
        return MAX_SCORE

    voronois = voronoi(state)

    for (player, voronoi_for_player) in enumerate(voronois):
        debug(f"voronoi for {player} : {voronoi_for_player}")

    score = voronois[me]

    return score


def voronoi(state: State) -> list[int]:
    """returns an array so that voronoi[player]=nb of cell player is the nearest of"""
    voronoi_state = state.copy()
    timer.start_step("voronoi")

    remaining = deque()
    for player, head in enumerate(state.heads):
        if head > -1:
            for (player, adjacent) in [(player, adjacent) for adjacent in state.get_valid_adjacent(head)]:
                remaining.appendleft((player, adjacent))

    counters = [0]*state.nb_players
    while bool(remaining):  # == is not empty
        (player, current) = remaining.pop()
        if voronoi_state.is_free(current):
            counters[player] += 1
            voronoi_state.set_cell(current, player + 4)
            for adjacent in voronoi_state.get_valid_adjacent(current):
                remaining.appendleft((player, adjacent))

    debug(f"Voronoi took {timer.stop_step('voronoi') * 1000:.3f} ms")
    voronoi_state.print()

    return counters


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

def compute_free_space_per_user(me, turn, state):
    nb_alive = state.get_nb_alive()
    nb_moves = turn * nb_alive
    for p in range(me):
        if state.is_player_alive(p):
            nb_moves += 1

    return ((WIDTH*HEIGHT) - nb_moves) / nb_alive


def game_loop():

    state = None
    turn = 0

    while True:
        # n: total number of players (2 to 4).
        # p: your player number (0 to 3).
        nb_players, me = [int(i) for i in input().split()]
        if turn == 0:
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
        #state.print(LOG_INFO)
        # (12,5)(1,5)
        free_space_per_user = compute_free_space_per_user(me, turn, state)
        if free_space_per_user > FREE_SPACE_PER_USER_THRESHOLD:
            debug(f'Over the free space per player threshold ({free_space_per_user}) : using minimax_one')
            direction = choose_minimax_one(me, state)
        else:
            debug(f'Below the free space per player threshold ({free_space_per_user}) : using minimax')
            direction = minimax(state, me, max_elapsed_time_ratio=MAX_TIME_RATIO, max_depth=MAX_DEPTH)

        debug(f"Going {direction_str(direction)} (time: {((timer.elapsed_time()) * 1000):.3f} ms)", LOG_WARN)

        print_direction(direction)

# config
LOG_THRESHOLD = LOG_INFO

hostname = socket.gethostname()
debug(f"Sys: {os.name} Platform: {platform.system()} Release: {platform.release()} Python: {platform.python_version()} Hostname: {hostname}", LOG_INFO)

on_codingame='codemachine' in hostname

if not on_codingame:
    debug("Not on codingame: set log lvl to DEBUG", LOG_INFO)
    LOG_THRESHOLD=LOG_DEBUG
else:
    debug("On codingame, log lvl = INFO", LOG_INFO)

# config
MAX_DEPTH = 5
MAX_TIME_RATIO = 0.05
MAX_ACCESSIBLE_COUNT = 50
ERROR_SCORE = -999999
FREE_SPACE_PER_USER_THRESHOLD=50

game_loop()