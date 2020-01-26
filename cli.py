# -*- coding: utf-8 -*-

import logging

import players
from framework import *

logging.basicConfig(format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

played_games = 0
gsum = 0
best_score = 0

learn = LearningState()
games_to_play = 10000
save = True

while played_games < games_to_play:
    played_games += 1

    p = [players.Reinforced(), players.Trustful(), players.Trustful(), players.Trustful(), players.Trustful()]

    learn.states_history = []
    game = Game(p, logger, log=False, learning_state=learn, save=save)

    while game.is_game_over() is False:
        game.make_move()

    gsum += sum(game.board_state.values())
    if sum(game.board_state.values()) > best_score:
        best_score = sum(game.board_state.values())

    if played_games % 10 == 0:
        print(played_games, gsum / played_games, best_score)

    if played_games % 1000 == 0 and save:
        learn.save_knowledge()

if save:
    learn.save_knowledge()

print(learn.score_history[0])
print(gsum / games_to_play)
