# -*- coding: utf-8 -*-

import logging
import bayes_opt
import players
from framework import *
from bayes_opt.observer import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs


def play_function(d0, d1, d2, g0, g1, g2, g3, g4, g5, g6, g7, r0, r1, r2, r3, r4, r5, r6, r7,
                  i0, i1, i2, i3, i4, i5, i6, i7):

    logging.basicConfig(format='%(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    played_games = 0
    gsum = 0

    parameters = BayesianParameters([d0, d1, d2], [g0, g1, g2, g3, g4, g5, g6, g7], [r0, r1, r2, r3, r4, r5, r6, r7],
                                    [i0, i1, i2, i3, i4, i5, i6, i7])

    games_to_play = 20
    while played_games < games_to_play:
        played_games += 1

        p = [players.TrustfulParamInjection(), players.TrustfulParamInjection(),
             players.TrustfulParamInjection(), players.TrustfulParamInjection()]

        game = Game(p, logger, log=False, learning_state=parameters)

        while game.is_game_over() is False:
            game.make_move()

        gsum += sum(game.board_state.values())

        if played_games % 10 == 0:
            print(played_games, gsum / played_games)

    return gsum / games_to_play


pbounds = {'d0': (0, 5), 'd1': (-10, 0), 'd2': (0.7, 1.5),
           'g0': (0, 5), 'g1': (0, 1), 'g2': (-10, 0), 'g3': (0.7, 1.5), 'g4': (0.8, 1.3),
           'g5': (-0.8, 0.8), 'g6': (-0.5, 1), 'g7': (0.9, 2),
           'r0': (0, 5), 'r1': (0, 1), 'r2': (-10, 0), 'r3': (0.7, 1.5), 'r4': (0.8, 1.3),
           'r5': (-0.8, 0.8), 'r6': (-0.5, 1), 'r7': (0.9, 2),
           'i0': (0, 5), 'i1': (0, 1), 'i2': (-10, 0), 'i3': (0.7, 1.5), 'i4': (0.8, 1.3),
           'i5': (-0.8, 0.8), 'i6': (-0.5, 1), 'i7': (0.9, 2)}

optimizer = bayes_opt.BayesianOptimization(
    f=play_function,
    pbounds=pbounds,
    verbose=2,
    random_state=1,
)

load_logs(optimizer, logs=["./logs.json"])
#logger1 = JSONLogger(path="./logs4.json")
#optimizer.subscribe(Events.OPTMIZATION_STEP, logger1)

print("New optimizer is now aware of {} points.".format(len(optimizer.space)))
# optimizer.maximize(
#    init_points=0,
#    n_iter=2000,
#)

results = []

for i, res in enumerate(optimizer.res):
    print("Iteration {}: \n\t{}".format(i, res['target']))
    results.append((i, res['target'], res['params']))

results = sorted(results, key=lambda x: x[1])
for result in results:
    st = "\n"
    a = 0
    for param in result[2]:
        a += 1
        st += str(result[2][param]) + ", "
        if a == 3 or a == 11 or a == 19 or a == 27:
            st += "\n"

    print(result[0], result[1], st)
