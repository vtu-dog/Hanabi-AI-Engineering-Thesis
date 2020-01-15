# -*- coding: utf-8 -*-


class BasePlayer:
    def __init__(self):
        self.name = 'BasePlayer'

    def __str__(self):
        return self.name

    def inject_info(self, player_number, logger, learning_state, name_suffix=''):
        self.player_number = player_number
        self.logger = logger
        self.learning = False
        self.learning_state = learning_state
        self.name += name_suffix

    def play(self, round_info):
        raise Exception('Player must override the "play" method')
