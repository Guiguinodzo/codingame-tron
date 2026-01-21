import sys

def debug(log):
    print(log, file=sys.stderr, flush=True)


turn = 0
while True:
    # n: total number of players (2 to 4).
    # p: your player number (0 to 3).
    nb_players, me = [int(i) for i in input().split()]
    debug(f"nb_players: {nb_players}, me: {me}")

    for player in range(nb_players):
        # x0: starting X coordinate of lightcycle (or -1)
        # y0: starting Y coordinate of lightcycle (or -1)
        # x1: starting X coordinate of lightcycle (can be the same as X0 if you play before this player)
        # y1: starting Y coordinate of lightcycle (can be the same as Y0 if you play before this player)
        x0, y0, x1, y1 = [int(j) for j in input().split()]
        debug(f"p{player} : x0, y0, x1, y1: {x0, y0, x1, y1}")

    print(['UP','DOWN','LEFT','RIGHT'][turn % 4])
    turn += 1
