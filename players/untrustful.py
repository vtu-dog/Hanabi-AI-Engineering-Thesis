# -*- coding: utf-8 -*-

from framework import BasePlayer, Choice, ChoiceDetails


class Distrustful(BasePlayer):
    def __init__(self, *args):
        super(Distrustful, self).__init__(*args)
        self.name = 'Untrustful'

    @staticmethod
    def check_for_play(self, round_info, player_number):
        best_card = 0
        for card in round_info.player_hand:
            if card.is_playable(round_info.board_state):
                if card.revealed_rank is 1 or card.reavealed_rank > best_card:
                    best_card = card.hand_position

        if best_card > 0:
            return ChoiceDetails(
                Choice.PLAY,
                best_card
            )
        return False

    @staticmethod
    def check_for_necessary_tip(self, round_info, player_number):
        return False

    @staticmethod
    def check_for_obvious_discard(self, round_info, player_number):
        lowest_rank = min(round_info.board_state.values())
        for card in round_info.player_hand:
            if (card.revealed_rank is not None and card.revealed_rank < lowest_rank) or \
               (card.revealed_suit is not None and round_info.board_state[card.revealed_suit] is 5) or \
               (card.revealed_suit is not None and card.revealed_rank is not None and
               round_info.board_state[card.revealed_suit] >= card.revealed_rank):
                return ChoiceDetails(
                    Choice.DISCARD,
                    card.hand_position
                )
        return False

    @staticmethod
    def check_for_tip(self, round_info):
        return False

    def play(self, round_info):
        action_order = [self.check_for_play, self.check_for_necessary_tip, self.check_for_obvious_discard,
                        self.check_for_good_tip, self.check_for_guess_discard]

        for action in action_order:
            decision = action(round_info)
            if decision is not False:
                return decision
