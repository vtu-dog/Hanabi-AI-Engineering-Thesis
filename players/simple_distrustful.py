# -*- coding: utf-8 -*-

import functools
import random
from framework import BasePlayer, Choice, ChoiceDetails, utils, HintDetails


class SimpleDistrustful(BasePlayer):
    def __init__(self, *args):
        super(SimpleDistrustful, self).__init__(*args)
        self.name = 'Simple Distrustful'

    def check_for_obvious_play(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        board_state_stars_align = round_info.board_state[utils.Suit.BLUE] + 1
        prev = False
        for suit in round_info.board_state:
            if prev is not False and round_info.board_state[suit] is not prev:
                board_state_stars_align = -1
            prev = round_info.board_state[suit]

        best_card = -1
        best_card_rank = 6

        for card in player_hand:
            if (card.is_playable(round_info) or
                (card.revealed_rank is not None and card.revealed_rank.value is board_state_stars_align)) and \
                    card.revealed_rank.value < best_card_rank:
                best_card = card.hand_position
                best_card_rank = card.revealed_rank.value

        if best_card >= 0:
            return ChoiceDetails(
                Choice.PLAY,
                best_card
            )
        return False

    def check_for_hint(self, round_info, player_number):
        if round_info.hints <= 1:
            return False

        original_player_number = player_number
        player_number = utils.next_player_number(round_info, original_player_number)
        hinted_plays = {}

        while player_number is not original_player_number:
            hinted_plays[player_number] = {}
            for suit in utils.Suit:
                hinted_plays[player_number][suit] = {}
                for rank in utils.Rank:
                    hinted_plays[player_number][suit][rank] = 0

            player_hand = utils.get_player_hand_by_number(round_info, player_number)
            for card in player_hand:
                if round_info.board_state[card.real_suit] < card.real_rank.value and \
                        (card.revealed_rank is not None or card.revealed_suit is not None):
                    hinted_plays[player_number][card.real_suit][card.real_rank] += 1

            player_number = utils.next_player_number(round_info, player_number)

        player_number = utils.next_player_number(round_info, original_player_number)

        best_hint_player = None
        best_hint_rank = 6
        best_hint_type = None

        while player_number is not original_player_number:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)
            for card in player_hand:
                already_hinted = False
                for player in hinted_plays:
                    if player is not player_number and hinted_plays[player][card.real_suit][card.real_rank] is not 0:
                        already_hinted = True
                if round_info.board_state[card.real_suit] < card.real_rank.value < best_hint_rank and \
                        not already_hinted:
                    if card.revealed_rank is None:
                        best_hint_player = player_number
                        best_hint_rank = card.real_rank.value
                        best_hint_type = card.real_rank
                    elif card.revealed_suit is None:
                        best_hint_player = player_number
                        best_hint_rank = card.real_rank.value
                        best_hint_type = card.real_suit

            player_number = utils.next_player_number(round_info, player_number)

        if best_hint_player is not None:
            return ChoiceDetails(
                Choice.HINT,
                HintDetails(best_hint_player, best_hint_type)
            )
        return False

    def check_for_discard(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        unmarked = []
        for card in player_hand:
            if card.revealed_rank is None and card.revealed_suit is None:
                unmarked.append(card)

        if len(unmarked) is 0:
            known = utils.list_all_known_cards(round_info, player_number)[0]
            remaining = utils.list_remaining_playable_cards(round_info)
            discarded = utils.list_discarded_cards(round_info)

            for card in player_hand:
                if card.revealed_rank is None:
                    add = True
                    for rank in utils.Rank:
                        if round_info.board_state[card.revealed_suit] < rank.value and \
                                remaining[card.revealed_suit][rank] is 1 and \
                                known[card.revealed_suit][rank] - discarded[card.revealed_suit][rank] is 0:
                            add = False
                    if add:
                        unmarked.append(card)

                elif card.revealed_suit is None:
                    add = True
                    for suit in utils.Suit:
                        if round_info.board_state[suit] < card.revealed_rank.value and \
                                remaining[suit][card.revealed_rank] is 1 and \
                                known[suit][card.revealed_rank] - discarded[suit][card.revealed_rank] is 0:
                            add = False
                    if add:
                        unmarked.append(card)

        if len(unmarked) is 0:
            unmarked = player_hand

        return ChoiceDetails(
            Choice.DISCARD,
            random.choice(unmarked).hand_position
        )

    def play(self, round_info):
        action_order = [self.check_for_obvious_play, self.check_for_hint, self.check_for_discard]

        for action in action_order:
            decision = functools.partial(action, round_info, round_info.player_turn)()
            if decision is not False:
                return decision
