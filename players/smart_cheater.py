# -*- coding: utf-8 -*-

import functools
from framework import BasePlayer, Choice, ChoiceDetails, utils, HintDetails


class SmartCheater(BasePlayer):
    def __init__(self, *args):
        super(SmartCheater, self).__init__(*args)
        self.name = 'Smart Cheater'

    def list_all_known_cards(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.true_hand_info()
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        known = {}
        for suit in utils.Suit:
            known[suit] = {}
            for rank in utils.Rank:
                known[suit][rank] = 0

        for card in player_hand:
            if card.real_rank is not None and card.real_suit is not None:
                known[card.real_suit][card.real_rank] += 1

        for hand in round_info.other_players_hands:
            if player_number is not hand.player_number:
                for card in hand:
                    known[card.real_suit][card.real_rank] += 1

        return known

    def check_for_play(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.true_hand_info()
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        known = self.list_all_known_cards(round_info, player_number)

        best_card = -1
        chain_bonus = False
        best_card_rank = 6
        for card in player_hand:
            if round_info.board_state[card.real_suit] + 1 is card.real_rank.value:
                new_chain = False
                if card.real_rank.value <= 4 and known[card.real_suit][utils.Rank(card.real_rank.value + 1)] > 0:
                    new_chain = True
                if (chain_bonus and new_chain and card.real_rank.value < best_card_rank) or \
                        (not chain_bonus and (new_chain or card.real_rank.value < best_card_rank)):
                    best_card = card.hand_position
                    best_card_rank = card.real_rank.value
                    chain_bonus = new_chain

        if best_card >= 0:
            return ChoiceDetails(
                Choice.PLAY,
                best_card
            )
        return False

    def check_card_usefulness(self, round_info, card):
        remaining = utils.list_remaining_playable_cards(round_info)

        point_of_uselessness = {}
        for suit in utils.Suit:
            point_of_uselessness[suit] = None
            for rank in utils.Rank:
                if round_info.board_state[suit] < rank.value:
                    if point_of_uselessness[suit] is None and remaining[suit][rank] is 0:
                        point_of_uselessness[suit] = rank

        if round_info.board_state[card.real_suit] < card.real_rank.value and \
                (point_of_uselessness[card.real_suit] is None or
                 point_of_uselessness[card.real_suit].value > card.real_rank.value):
            useless = False
        else:
            useless = True

        if useless:
            return ChoiceDetails(
                Choice.DISCARD,
                card.hand_position
            )
        return False

    def check_for_obvious_discard(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.true_hand_info()
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        for card in player_hand:
            answer = self.check_card_usefulness(round_info, card)
            if answer is not False:
                return answer
        return False

    def check_for_forced_discard(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.true_hand_info()
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        known = self.list_all_known_cards(round_info, player_number)
        remaining = utils.list_remaining_playable_cards(round_info)

        for card in player_hand:
            if known[card.real_suit][card.real_rank] > 1:
                return ChoiceDetails(
                    Choice.DISCARD,
                    card.hand_position
                )

        for card in player_hand:
            if remaining[card.real_suit][card.real_rank] > 1:
                return ChoiceDetails(
                    Choice.DISCARD,
                    card.hand_position
                )

        best_card_rank = -1
        best_card = None
        for card in player_hand:
            if card.real_rank.value > best_card_rank:
                best_card = card.hand_position
                best_card_rank = card.real_rank.value

        return ChoiceDetails(
            Choice.DISCARD,
            best_card
        )

    def hint_first_free_card(self, round_info, player_number):
        original_player_number = player_number
        player_number = utils.next_player_number(round_info, player_number)

        while player_number is not original_player_number:
            if player_number is round_info.player_turn:
                player_hand = round_info.true_hand_info()
            else:
                player_hand = utils.get_player_hand_by_number(round_info, player_number)

            for card in player_hand:
                if card.revealed_rank is None:
                    return ChoiceDetails(
                        Choice.HINT,
                        HintDetails(player_number, card.real_rank)
                    )
                elif card.revealed_suit is None:
                    return ChoiceDetails(
                        Choice.HINT,
                        HintDetails(player_number, card.real_suit)
                    )
            player_number = utils.next_player_number(round_info, player_number)

    def check_for_soft_pass_turn(self, round_info, player_number):
        original_player_number = player_number
        player_number = utils.next_player_number(round_info, player_number)

        needed_passes = 1
        while player_number is not original_player_number:
            if not self.check_for_obvious_discard(round_info, player_number):
                needed_passes += 1
            player_number = utils.next_player_number(round_info, player_number)

        if round_info.hints <= needed_passes:
            return False
        else:
            return self.hint_first_free_card(round_info, player_number)

    def check_for_hard_pass_turn(self, round_info, player_number):
        if round_info.hints > 0:
            return self.hint_first_free_card(round_info, player_number)
        else:
            return False

    def play(self, round_info):
        action_order = [self.check_for_play, self.check_for_soft_pass_turn, self.check_for_obvious_discard,
                        self.check_for_hard_pass_turn, self.check_for_forced_discard]

        for action in action_order:
            decision = functools.partial(action, round_info, round_info.player_turn)()
            if decision is not False:
                return decision
