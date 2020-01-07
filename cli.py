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

games_to_play = 1000
while played_games < games_to_play:
    played_games += 1

    #p = [players.Trustful(), players.Trustful(),
    #     players.Trustful(), players.Trustful()]
    p = [players.SmartCheater(), players.SmartCheater(),
         players.SmartCheater(), players.SmartCheater()]

    game = Game(p, None, log=False)

    while game.is_game_over() is False:
        game.make_move()

    gsum += sum(game.board_state.values())

    if played_games % 10 == 0:
        print(played_games, gsum / played_games)


print(gsum / games_to_play)
