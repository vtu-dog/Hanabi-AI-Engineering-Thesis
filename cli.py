# -*- coding: utf-8 -*-

import logging

import players
from framework import *

logging.basicConfig(format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#players = [players.Distrustful(), players.Distrustful()]

played_games = 0
gsum = 0

games_to_play = 1
best_score = 0
while played_games < games_to_play:
    played_games += 1

    p = [players.Reinforced(), players.Reinforced(),
         players.Reinforced(), players.Reinforced()]

    game = Game(p, logger, log=True)

    while game.is_game_over() is False:
        game.make_move()

    gsum += sum(game.board_state.values())
    if sum(game.board_state.values()) > best_score:
        best_score = sum(game.board_state.values())

    if played_games % 10 == 0:
        print(played_games, gsum / played_games, best_score)


print(gsum / games_to_play)
