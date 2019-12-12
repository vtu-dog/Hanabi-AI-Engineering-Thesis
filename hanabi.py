# -*- coding: utf-8 -*-

import logging

import players
from framework import *


logging.basicConfig(format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

players = [players.Distrustful(), players.Distrustful(),
           players.Distrustful(), players.Distrustful()]
game = Game(players, logger, log=True)

while game.is_game_over() is False:
    game.make_move()
