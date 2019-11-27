# -*- coding: utf-8 -*-

from random import choice
from framework import BasePlayer, Choice, ChoiceDetails


class Cheater(BasePlayer):
    def __init__(self, *args):
        super(Cheater, self).__init__(*args)
        self.name = 'Cheater'

    def play(self, round_info):
        possible_plays = round_info.true_hand_info().playable_cards(round_info)

        if len(possible_plays) == 0:
            return ChoiceDetails(
                Choice.DISCARD,
                choice(round_info.player_hand).hand_position
            )

        else:
            return ChoiceDetails(
                Choice.PLAY,
                choice(possible_plays).hand_position
            )

        """
        # hint example:
        from framework import HintDetails, Suit
        return ChoiceDetails(Choice.HINT, HintDetails(abs(round_info.player_turn - 1), Suit.GREEN))
        """
