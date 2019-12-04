# -*- coding: utf-8 -*-

from framework import BasePlayer, Choice, ChoiceDetails, utils, HintDetails, Card


class Distrustful(BasePlayer):
    def __init__(self, *args):
        super(Distrustful, self).__init__(*args)
        self.name = 'Untrustful'

    @staticmethod
    def check_for_obvious_play(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        best_card = 0
        for card in player_hand:
            if card.is_playable(round_info):
                if card.revealed_rank is 1 or card.reavealed_rank > best_card:
                    best_card = card.hand_position

        if best_card > 0:
            return ChoiceDetails(
                Choice.PLAY,
                best_card
            )
        return False

    @staticmethod
    def check_for_obvious_discard(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        lowest_rank = min(round_info.board_state.values())
        for card in player_hand:  # To be upgraded to count from all known cards
            if (card.revealed_rank is not None and card.revealed_rank <= lowest_rank) or \
                    (card.revealed_suit is not None and round_info.board_state[card.revealed_suit] is 5) or \
                    (card.revealed_suit is not None and card.revealed_rank is not None and
                     round_info.board_state[card.revealed_suit] >= card.revealed_rank):
                return ChoiceDetails(
                    Choice.DISCARD,
                    card.hand_position
                )
        return False

    @staticmethod
    def check_for_guess_discard(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        unmarked = []
        for card in player_hand:
            if card.revealed_rank is None and card.reavealed_suit is None:
                unmarked.append(card)

        if len(unmarked) is 0:
            known = utils.list_all_known_cards(round_info)[0]
            remaining = utils.list_remaining_playable_cards(round_info)
            discarded = utils.list_discarded_cards(round_info)
            for card in player_hand:
                if card.revealed_rank is None:
                    add = True
                    for rank in card.Rank:
                        if round_info.board_state[card.revealed_suit] < rank and \
                                remaining[card.revealed_suit][rank] is 1 and \
                                known[card.revealed_suit][rank] - discarded[card.revealed_suit][rank] is 0:
                            add = False
                        if add:
                            unmarked.append(card)

                elif card.revealed_suit is None:
                    add = True
                    for suit in remaining:
                        if round_info.board_state[suit] < card.revealed_rank and \
                                remaining[suit][card.revealed_rank] is 1 and \
                                known[suit][card.revealed_rank] - discarded[suit][card.revealed_rank] is 0:
                            add = False
                    if add:
                        unmarked.append(card)

        if len(unmarked) is 0:
            unmarked = player_hand

        oldest = unmarked[0]
        for card in unmarked:
            if card.drawn_on_turn < oldest.drawn_on_turn:
                oldest = card
        return ChoiceDetails(
            Choice.DISCARD,
            oldest.hand_position
        )

    @staticmethod
    def check_for_necessary_tip(self, round_info, player_number):
        if round_info.hints is 0:
            return False

        remaining = utils.list_remaining_playable_cards(round_info)
        next_player_hand = utils.next_player_hand(round_info, player_number)
        next_player_number = utils.next_player_number(round_info, player_number)
        discarded_position = self.check_for_guess_discard(round_info, next_player_number)[1]
        discarded = next_player_hand[discarded_position]

        if round_info.board_state[discarded.suit] < discarded.rank and remaining[discarded.suit][discarded.rank] is 1:
            return ChoiceDetails(
                Choice.HINT,
                HintDetails(utils.next_player_number(round_info, player_number), discarded.rank)
            )
        return False

    @staticmethod
    def check_for_good_tip(self, round_info):
        return False

    def play(self, round_info):
        action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_obvious_discard,
                        self.check_for_good_tip, self.check_for_guess_discard]

        for action in action_order:
            decision = action(round_info, round_info.player_turn)
            if decision is not False:
                return decision
