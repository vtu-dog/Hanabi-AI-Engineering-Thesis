# -*- coding: utf-8 -*-

import functools
import random
from copy import deepcopy

from framework import BasePlayer, Choice, ChoiceDetails, utils, HintDetails


class StoppedClock(BasePlayer):
    def __init__(self, *args):
        super(StoppedClock, self).__init__(*args)
        self.name = 'Stopped Clock'

    def check_for_play(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        for card in player_hand:
            if card.revealed_rank is not None and card.revealed_suit is not None and \
                    round_info.board_state[card.revealed_suit] + 1 is card.revealed_rank.value:
                return ChoiceDetails(
                    Choice.PLAY,
                    card.hand_position
                )
        return False

    def check_for_discard(self, round_info, player_number):
        if round_info.hints is utils.MAX_HINTS:
            return False

        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        unmarked = []
        for card in player_hand:
            if card.revealed_rank is None and card.revealed_suit is None:
                unmarked.append(card)

        if len(unmarked) is 0:
            for card in player_hand:
                if card.revealed_rank is None or card.revealed_suit is None:
                    unmarked.append(card)

        if len(unmarked) is 0:
            unmarked = player_hand

        return ChoiceDetails(
            Choice.DISCARD,
            random.choice(unmarked).hand_position
        )

    def check_for_hint(self, round_info, player_number):
        if round_info.hints is 0:
            return False

        players = list(range(0, round_info.number_of_players))
        random.shuffle(players)
        for player in players:
            if player is not player_number:
                hand = deepcopy(utils.get_player_hand_by_number(round_info, player))
                hand.shuffle()
                for card in hand:
                    if random.randint(0,1) is 0:
                        if card.revealed_rank is None:
                            return ChoiceDetails(
                                Choice.HINT,
                                HintDetails(player, card.real_rank)
                            )
                        elif card.revealed_suit is None:
                            return ChoiceDetails(
                                Choice.HINT,
                                HintDetails(player, card.real_suit)
                            )
                    else:
                        if card.revealed_suit is None:
                            return ChoiceDetails(
                                Choice.HINT,
                                HintDetails(player, card.real_suit)
                            )
                        elif card.revealed_rank is None:
                            return ChoiceDetails(
                                Choice.HINT,
                                HintDetails(player, card.real_rank)
                            )

        for player in players:
            if player is not player_number:
                hand = utils.get_player_hand_by_number(round_info, player)
                for card in hand:
                    return ChoiceDetails(
                        Choice.HINT,
                        HintDetails(player, card.real_suit)
                    )

    def play(self, round_info):
        action_order = [self.check_for_play, self.check_for_hint, self.check_for_discard]
        random.shuffle(action_order)

        for action in action_order:
            decision = functools.partial(action, round_info, round_info.player_turn)()
            if decision is not False:
                return decision
