# -*- coding: utf-8 -*-

from framework import BasePlayer, Choice, ChoiceDetails, utils, HintDetails, Card
import functools


class Distrustful(BasePlayer):
    def __init__(self, *args):
        super(Distrustful, self).__init__(*args)
        self.name = 'Distrustful'

    def check_for_obvious_play(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        best_card = 0
        best_card_rank = 6
        for card in player_hand:
            if card.is_playable(round_info) and card.revealed_rank.value < best_card_rank:
                best_card = card.hand_position
                best_card_rank = card.revealed_rank.value

        if best_card > 0:
            return ChoiceDetails(
                Choice.PLAY,
                best_card
            )
        return False

    def check_for_obvious_discard(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        lowest_rank = min(round_info.board_state.values())
        for card in player_hand:  # To be upgraded to count from all known cards
            if (card.revealed_rank is not None and card.revealed_rank.value <= lowest_rank) or \
                    (card.revealed_suit is not None and round_info.board_state[card.revealed_suit] is 5) or \
                    (card.revealed_suit is not None and card.revealed_rank is not None and
                     round_info.board_state[card.revealed_suit] >= card.revealed_rank.value):
                return ChoiceDetails(
                    Choice.DISCARD,
                    card.hand_position
                )
        return False

    def check_for_guess_discard(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)
        unmarked = []
        for card in player_hand:
            if card.revealed_rank is None and card.revealed_suit is None:
                unmarked.append(card)

        if len(unmarked) is 0:
            known = utils.list_all_known_cards(round_info)[0]
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
                    for suit in remaining:
                        if round_info.board_state[suit] < card.revealed_rank.value and \
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

    def check_for_necessary_tip(self, round_info, player_number):
        if round_info.hints is 0:
            return False

        remaining = utils.list_remaining_playable_cards(round_info)
        next_player_hand = utils.next_player_hand(round_info, player_number)
        next_player_number = utils.next_player_number(round_info, player_number)
        discarded_position = self.check_for_guess_discard(round_info, next_player_number)[1]
        discarded = next_player_hand[discarded_position]

        if round_info.board_state[discarded.real_suit] < discarded.real_rank.value and \
                remaining[discarded.real_suit][discarded.real_rank] is 1:
            if discarded.revealed_rank is None:
                return ChoiceDetails(
                    Choice.HINT,
                    HintDetails(utils.next_player_number(round_info, player_number), discarded.real_rank)
                )
            else:
                return ChoiceDetails(
                    Choice.HINT,
                    HintDetails(utils.next_player_number(round_info, player_number), discarded.real_suit)
                )
        return False

    def check_for_play_tip(self, round_info, player_number, hint_pass_score=2, double_hint_multiplier=2,
                           distance_to_playable_multiplier=0.95, distance_to_player_multiplier=0.95):
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
        potential_playable_ranks = {}
        potential_playable_suits = {}

        while player_number is not original_player_number:
            potential_playable_ranks[player_number] = {}
            potential_playable_suits[player_number] = {}
            for rank in utils.Rank:
                potential_playable_ranks[player_number][rank] = []
            for suit in utils.Suit:
                potential_playable_suits[player_number][suit] = []

            player_hand = utils.get_player_hand_by_number(round_info, player_number)
            for card in player_hand:
                already_hinted = False
                for player in hinted_plays:
                    if player is not player_number and hinted_plays[player][card.real_suit][card.real_rank] is not 0:
                        already_hinted = True
                if round_info.board_state[card.real_suit] < card.real_rank.value and not already_hinted:
                    if card.revealed_suit is None:
                        potential_playable_suits[player_number][card.real_suit].append(card)
                    if card.revealed_rank is None:
                        potential_playable_ranks[player_number][card.real_rank].append(card)

            player_number = utils.next_player_number(round_info, player_number)

        max_player_number = 0
        max_potential = 0
        max_hint = 0

        def check_card_potential(card, player):
            player_distance = player - original_player_number - 1
            if player_distance < 0:
                player_distance += round_info.number_of_players
            card_potential = \
                pow(distance_to_playable_multiplier, card.real_rank.value-round_info.board_state[card.real_suit]-1) *\
                pow(distance_to_player_multiplier, player_distance)
            if card.revealed_suit is not None and round_info.board_state[card.real_suit] - card.real_rank.value is 1:
                card_potential *= double_hint_multiplier
            return card_potential

        for player in potential_playable_ranks:
            for rank in potential_playable_ranks[player]:
                potential = 0
                for card in potential_playable_ranks[player][rank]:
                    potential += check_card_potential(card, player)
                if potential > max_potential:
                    max_player_number = player
                    max_potential = potential
                    max_hint = rank

            for suit in potential_playable_suits[player]:
                potential = 0
                for card in potential_playable_suits[player][suit]:
                    potential += check_card_potential(card, player)
                if potential > max_potential:
                    max_player_number = player
                    max_potential = potential
                    max_hint = suit

        if max_potential >= hint_pass_score:
            return ChoiceDetails(
                Choice.HINT,
                HintDetails(max_player_number, max_hint)
            )

        return False

    def check_for_discard_tip(self, round_info, player_number, hint_pass_score=2.5, distance_to_player_multiplier=0.95):
        original_player_number = player_number
        player_number = utils.next_player_number(round_info, original_player_number)

        potential_discardable_ranks = {}
        potential_discardable_suits = {}
        while player_number is not original_player_number:
            potential_discardable_ranks[player_number] = {}
            potential_discardable_suits[player_number] = {}
            for rank in utils.Rank:
                potential_discardable_ranks[player_number][rank] = []
            for suit in utils.Suit:
                potential_discardable_suits[player_number][suit] = []

            player_hand = utils.get_player_hand_by_number(round_info, player_number)
            for card in player_hand:
                if round_info.board_state[card.real_suit] >= card.real_rank.value:
                    if card.revealed_suit is None:
                        potential_discardable_suits[player_number][card.real_suit].append(card)
                    if card.revealed_rank is None:
                        potential_discardable_ranks[player_number][card.real_rank].append(card)
            player_number = utils.next_player_number(round_info, player_number)

        max_player_number = 0
        max_potential = 0
        max_hint = 0

        def check_card_potential(card, player):
            player_distance = player - original_player_number - 1
            if player_distance < 0:
                player_distance += round_info.number_of_players
            card_potential = pow(distance_to_player_multiplier, player_distance)
            return card_potential

        for player in potential_discardable_ranks:
            for rank in potential_discardable_ranks[player]:
                potential = 0
                for card in potential_discardable_ranks[player][rank]:
                    potential += check_card_potential(card, player)
                if potential > max_potential:
                    max_player_number = player
                    max_potential = potential
                    max_hint = rank

            for suit in potential_discardable_suits[player]:
                potential = 0
                for card in potential_discardable_suits[player][suit]:
                    potential += check_card_potential(card, player)
                if potential > max_potential:
                    max_player_number = player
                    max_potential = potential
                    max_hint = suit

        if max_potential >= hint_pass_score:
            return ChoiceDetails(
                Choice.HINT,
                HintDetails(max_player_number, max_hint)
            )

        return False

    def check_for_good_tip(self, round_info, player_number):
        play_tip = self.check_for_play_tip(round_info, player_number)
        if play_tip is not False:
            return play_tip

        discard_tip = self.check_for_discard_tip(round_info, player_number)
        return discard_tip

    def check_for_mediocre_tip(self, round_info, player_number):
        return self.check_for_play_tip(round_info, player_number, 1, 2)

    def play(self, round_info):
        if round_info.hints is utils.MAX_HINTS:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_good_tip,
                            self.check_for_mediocre_tip, self.check_for_obvious_discard, self.check_for_guess_discard]
        elif round_info.hints >= 3:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_obvious_discard,
                            self.check_for_good_tip, self.check_for_mediocre_tip, self.check_for_guess_discard]
        else:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_obvious_discard,
                            self.check_for_good_tip, self.check_for_guess_discard]

        for action in action_order:
            decision = functools.partial(action, round_info, round_info.player_turn)()
            if decision is not False:
                return decision
