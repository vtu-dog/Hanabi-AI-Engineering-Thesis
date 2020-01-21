# -*- coding: utf-8 -*-

from framework import BasePlayer, Choice, ChoiceDetails, utils, HintDetails
import functools
import bayes_opt
from copy import deepcopy

debug = False


class BayesianTrustful(BasePlayer):
    def __init__(self, *args):
        super(BayesianTrustful, self).__init__(*args)
        self.name = 'Bayesian Trustful'
        self.card_hint_type = {}
        self.discard_tip = []
        self.good_tip = []
        self.risky_tip = []
        self.information_tip = []
        self.hand_size = 5

    def initialize_card_hint_history(self, round_info):
        original_player_number = round_info.player_turn
        player_number = original_player_number
        just_began = True

        self.hand_size = len(round_info.player_hand)

        while just_began or player_number is not original_player_number:
            just_began = False
            self.card_hint_type[player_number] = []
            for x in range(len(round_info.player_hand)):
                self.card_hint_type[player_number].append(None)
            player_number = utils.next_player_number(round_info, player_number)

        self.discard_tip = self.learning_state.discard_tip_parameters
        self.good_tip = self.learning_state.good_tip_parameters
        self.risky_tip = self.learning_state.risky_tip_parameters
        self.information_tip = self.learning_state.information_tip_parameters

    def extrapolate_board_state(self, round_info, target_player):
        player_number = utils.next_player_number(round_info, round_info.player_turn)
        predicted_board_state = deepcopy(round_info.board_state)

        while player_number is not target_player:
            play = self.check_for_obvious_play(round_info, player_number)
            if play is False:
                play = self.check_for_hinted_play(round_info, player_number)
            if play is not False:
                player_hand = utils.get_player_hand_by_number(round_info, player_number)
                suit = player_hand[play[1]].real_suit
                rank = player_hand[play[1]].real_rank
                self.info("{0} {1}".format(suit, rank))
                if suit is None or rank is None or predicted_board_state[suit] is rank.value - 1:
                    predicted_board_state[suit] += 1

            player_number = utils.next_player_number(round_info, player_number)

        return predicted_board_state

    def check_play_history(self, round_info):
        original_player_number = round_info.player_turn
        player_number = original_player_number
        amount_of_players = len(self.card_hint_type)
        current_board_state = deepcopy(round_info.board_state)
        current_lives = round_info.lives
        current_hints = round_info.hints
        current_discarded = round_info.discarded
        current_played = round_info.played

        for i in range(-1, -amount_of_players - 1, -1):
            if len(round_info.history) + i >= 0:
                move = round_info.history[i]

                if move[0] is Choice.PLAY:
                    if move[2].real_rank.value is current_board_state[move[2].real_suit]:
                        if current_board_state[move[2].real_suit] is 5:
                            current_hints = max(0, current_hints - 1)
                        current_board_state[move[2].real_suit] -= 1
                        current_played.pop()
                    else:
                        current_discarded.pop()
                        current_lives = min(utils.LIVES, current_lives + 1)

                if move[0] is Choice.DISCARD:
                    current_discarded.pop()
                    current_hints = max(0, current_hints - 1)

                if move[0] is Choice.HINT:
                    current_hints = min(current_hints + 1, utils.MAX_HINTS)

        for i in range(-amount_of_players, 0):
            if len(round_info.history) + i >= 0:
                move = round_info.history[i]
                if debug and round_info.log:
                    self.info("{0}, {1}, {2}, {3}, {4}".format(player_number, move[0], move[1], move[2], move[3]))

                if move[0] is Choice.PLAY or move[0] is Choice.DISCARD:
                    if debug and round_info.log:
                        self.info("{0}".format(self.card_hint_type[player_number][move[1]]))

                    if move[0] is Choice.PLAY:
                        if move[2].real_rank.value is current_board_state[move[2].real_suit] + 1:
                            current_board_state[move[2].real_suit] += 1
                            if current_board_state[move[2].real_suit] is 5:
                                current_hints = min(current_hints + 1, utils.MAX_HINTS)
                            current_played.append(move[2])
                        else:
                            current_discarded.append(move[2])
                            current_lives = max(1, current_lives - 1)

                    if move[0] is Choice.DISCARD:
                        current_hints = min(utils.MAX_HINTS, current_hints + 1)
                        current_discarded.append(move[2])

                    self.card_hint_type[player_number][move[1]] = None
                    if move[3] is 0:
                        for x in range(move[1], self.hand_size - 1):
                            self.card_hint_type[player_number][x] = self.card_hint_type[player_number][x + 1]

                if move[0] is Choice.HINT:
                    target_player = move[1]
                    hint = move[2]
                    hint_type = "Play"

                    current_round_info = deepcopy(round_info)
                    current_round_info.player_turn = player_number
                    current_round_info.board_state = deepcopy(current_board_state)
                    current_round_info.lives = current_lives
                    current_round_info.hints = current_hints
                    current_round_info.played = current_played
                    current_round_info.discarded = current_discarded
                    current_round_info.other_players_hands = []
                    hands = deepcopy(round_info.hands_history[i - 1])
                    for hand in hands:
                        if hand.player_number is player_number:
                            current_round_info.player_hand = hand
                        else:
                            current_round_info.other_players_hands.append(hand)

                    player_distance = target_player - player_number - 1
                    if player_distance < 0:
                        player_distance += round_info.number_of_players
                    if debug and round_info.log:
                        self.info("{0}".format(round_info.player_hand))
                        self.info("{0}, C: {1}, N: {2}".format(player_distance, current_round_info.player_hand,
                                                               current_round_info.other_players_hands[
                                                                   0].current_knowledge()))

                    if target_player is original_player_number:
                        player_hand = round_info.player_hand
                    else:
                        player_hand = round_info.hands_history[i][target_player]

                    if player_distance is 0:
                        answer = self.check_for_obvious_play(current_round_info, target_player)
                        if answer is False:
                            answer = self.check_for_hinted_play(current_round_info, target_player)
                            if answer is not False:
                                if debug and round_info.log:
                                    self.info("{0}".format(answer))
                                position = answer[1]
                                self.card_hint_type[target_player][position] = "Information"
                                if player_hand[position].revealed_rank is not None and \
                                        player_hand[position].revealed_suit is not None:
                                    hint_type = "Information"
                            else:
                                answer = self.check_for_guess_discard(current_round_info, target_player)
                                if debug and round_info.log:
                                    self.info("{0}".format(answer))
                                position = answer[1]
                                if isinstance(hint, utils.Rank):
                                    if player_hand[position].revealed_rank is not None and \
                                            player_hand[position].revealed_rank is hint:
                                        hint_type = "Information"
                                else:
                                    if player_hand[position].revealed_suit is not None and \
                                            player_hand[position].revealed_suit is hint:
                                        hint_type = "Information"

                    if isinstance(hint, utils.Rank) and max(current_board_state.values()) < hint.value - 1:
                        hint_type = "Information"

                    for x in range(0, len(player_hand)):
                        if isinstance(hint, utils.Rank):
                            if player_hand[x].revealed_rank is not None and player_hand[x].revealed_rank is hint:
                                if self.card_hint_type[target_player][x] is None:
                                    self.card_hint_type[target_player][x] = hint_type
                                elif player_hand[x].revealed_suit is not None:
                                    self.card_hint_type[target_player][x] = None
                        else:
                            if player_hand[x].revealed_suit is not None and player_hand[x].revealed_suit is hint:
                                if self.card_hint_type[target_player][x] is None:
                                    self.card_hint_type[target_player][x] = hint_type
                                elif player_hand[x].revealed_rank is not None:
                                    self.card_hint_type[target_player][x] = None

                    current_hints = max(0, current_hints - 1)
                    if debug and round_info.log:
                        self.info("{0}".format(hint_type))

            player_number = utils.next_player_number(round_info, player_number)

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
            if ((card.revealed_rank is not None and card.revealed_suit is not None and
                 round_info.board_state[card.revealed_suit] + 1 is card.revealed_rank.value) or
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

    def check_for_hinted_play(self, round_info, player_number):
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        alignment_delta = 2
        max_hint_size = 10

        if round_info.lives == 1:
            alignment_delta = 0
            max_hint_size = 1

        hinted_ranks = {}
        hinted_suits = {}
        for suit in utils.Suit:
            hinted_suits[suit] = 0
        for rank in utils.Rank:
            hinted_ranks[rank] = 0

        for x in range(0, len(player_hand)):
            if player_hand[x].revealed_suit is not None and player_hand[x].revealed_rank is None and \
                    self.card_hint_type[player_number][x] is "Play":
                hinted_suits[player_hand[x].revealed_suit] += 1
            if player_hand[x].revealed_rank is not None and player_hand[x].revealed_suit is None and \
                    self.card_hint_type[player_number][x] is "Play":
                hinted_ranks[player_hand[x].revealed_rank] += 1

        known = utils.list_all_known_cards(round_info, player_number)[0]
        remaining = utils.list_remaining_playable_cards(round_info)
        discarded = utils.list_discarded_cards(round_info)

        best_hint = -1
        best_hint_size = max_hint_size
        best_alignment = 0
        hint_type = None

        for suit in hinted_suits:
            if 0 < hinted_suits[suit] <= best_hint_size:
                rank = round_info.board_state[suit] + 1
                if rank <= 5:
                    rank_rank = utils.Rank(rank)
                    if remaining[suit][rank_rank] - known[suit][rank_rank] + discarded[suit][rank_rank] > 0:
                        best_hint = suit
                        best_hint_size = hinted_suits[suit]
                        best_alignment = 1
                        hint_type = 'suit'

        board_alignment = {}
        for rank in utils.Rank:
            board_alignment[rank] = 0
        for suit in round_info.board_state:
            rank = round_info.board_state[suit] + 1
            if rank <= 5:
                rank_rank = utils.Rank(rank)
                if remaining[suit][rank_rank] - known[suit][rank_rank] + discarded[suit][rank_rank] > 0:
                    board_alignment[rank_rank] += 1

        for rank in hinted_ranks:
            if 0 < board_alignment[rank] and ((0 < hinted_ranks[rank] < best_hint_size) or
                                              (0 < hinted_ranks[rank] <= best_hint_size and best_alignment <
                                               board_alignment[rank])):
                best_hint = rank
                best_hint_size = hinted_ranks[rank]
                best_alignment = board_alignment[rank]
                hint_type = 'rank'

        if best_hint is not -1 and best_hint_size <= best_alignment + alignment_delta:
            for x in range(0, len(player_hand)):
                if hint_type == 'rank':
                    if player_hand[x].revealed_rank is not None and player_hand[x].revealed_suit is None and \
                            player_hand[x].revealed_rank is best_hint and \
                            self.card_hint_type[player_number][x] is "Play":
                        return ChoiceDetails(
                            Choice.PLAY,
                            x
                        )
                else:
                    if player_hand[x].revealed_suit is not None and player_hand[x].revealed_rank is None and \
                            player_hand[x].revealed_suit is best_hint and \
                            self.card_hint_type[player_number][x] is "Play":
                        return ChoiceDetails(
                            Choice.PLAY,
                            x
                        )

        return False

    def check_card_usefulness(self, round_info, card):
        remaining = utils.list_remaining_playable_cards(round_info)
        useless = False

        point_of_uselessness = {}
        for suit in utils.Suit:
            point_of_uselessness[suit] = None
            for rank in utils.Rank:
                if round_info.board_state[suit] < rank.value:
                    if point_of_uselessness[suit] is None and remaining[suit][rank] is 0:
                        point_of_uselessness[suit] = rank

        if card.revealed_suit is not None:
            if round_info.board_state[card.revealed_suit] is 5 or \
                    (point_of_uselessness[card.revealed_suit] is not None and
                     round_info.board_state[card.revealed_suit] + 1 is point_of_uselessness[card.revealed_suit].value):
                useless = True

        if card.revealed_rank is not None:
            useless = True
            for suit in utils.Suit:
                if round_info.board_state[suit] < card.revealed_rank.value and \
                        (point_of_uselessness[suit] is None or
                         point_of_uselessness[suit].value > card.revealed_rank.value):
                    useless = False

        if card.revealed_suit is not None and card.revealed_rank is not None:
            if round_info.board_state[card.revealed_suit] < card.revealed_rank.value and \
                    (point_of_uselessness[card.revealed_suit] is None or
                     point_of_uselessness[card.revealed_suit].value > card.revealed_rank.value):
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
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        for card in player_hand:
            answer = self.check_card_usefulness(round_info, card)
            if answer is not False:
                return answer
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
        if round_info.hints is 0 or round_info.hints is utils.MAX_HINTS:
            return False

        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        remaining = utils.list_remaining_playable_cards(round_info)
        next_player_hand = utils.next_player_hand(round_info, player_number)
        next_player_number = utils.next_player_number(round_info, player_number)

        if self.check_for_obvious_play(round_info, next_player_number) is not False:
            return False

        distrust = False
        play = self.check_for_hinted_play(round_info, next_player_number)
        if play is not False:
            play_position = play[1]
            played_card = next_player_hand[play_position]

            if round_info.board_state[played_card.real_suit] is not played_card.real_rank.value - 1:
                distrust = True

                own_play = None
                if self.check_for_obvious_play(round_info, player_number) is not False:
                    own_play = self.check_for_obvious_play(round_info, player_number)[1]
                if own_play is None and self.check_for_hinted_play(round_info, player_number) is not False:
                    own_play = self.check_for_hinted_play(round_info, player_number)[1]

                if own_play is not None and \
                        round_info.board_state[played_card.real_suit] is played_card.real_rank.value - 2:
                    own_card = player_hand[own_play]
                    if (own_card.revealed_rank is not None and
                        own_card.revealed_rank.value is played_card.real_rank.value - 1) or \
                            (own_card.revealed_suit is not None and
                             own_card.revealed_suit is played_card.real_suit):
                        distrust = False

        else:
            if self.check_for_obvious_discard(round_info, next_player_number) is False:
                played_position = self.check_for_guess_discard(round_info, next_player_number)[1]
                played_card = next_player_hand[played_position]

                if round_info.board_state[played_card.real_suit] < played_card.real_rank.value and \
                        remaining[played_card.real_suit][played_card.real_rank] is 1 and \
                        self.check_card_usefulness(round_info, played_card) is False:
                    distrust = True

        if distrust:
            if debug and round_info.log:
                self.info("good_tip:")
            answer = self.check_for_good_tip(round_info, player_number, only_next_player=True)
            if answer is False:
                if debug and round_info.log:
                    self.info("risky_tip:")
                answer = self.check_for_risky_tip(round_info, player_number, only_next_player=True)

            if answer is not False:
                return answer

            if played_card.revealed_rank is None:
                return ChoiceDetails(
                    Choice.HINT,
                    HintDetails(utils.next_player_number(round_info, player_number), played_card.real_rank)
                )
            else:
                return ChoiceDetails(
                    Choice.HINT,
                    HintDetails(utils.next_player_number(round_info, player_number), played_card.real_suit)
                )

        return False

    def check_for_play_tip(self, round_info, player_number, hint_pass_score=0.9, double_hint_multiplier=0.3,
                           false_tip_penalty=-2.5, distance_to_player_multiplier=1.01, lower_rank_multiplier=1.07,
                           information_tip_value=0.2, already_has_play_multiplier=0.5, chain_bonus_multiplier=1.3,
                           only_next_player=False):
        if round_info.hints <= 1:
            return False

        original_player_number = player_number
        if player_number is round_info.player_turn:
            original_player_hand = round_info.player_hand
        else:
            original_player_hand = utils.get_player_hand_by_number(round_info, player_number)

        player_number = utils.next_player_number(round_info, original_player_number)
        worth_hinting = {}
        predicted_board_state = {original_player_number: deepcopy(round_info.board_state)}

        while player_number is not original_player_number:
            predicted_board_state[player_number] = deepcopy(
                predicted_board_state[utils.prev_player_number(round_info, player_number)])
            worth_hinting[player_number] = False

            play = self.check_for_obvious_play(round_info, player_number)
            if play is False:
                play = self.check_for_hinted_play(round_info, player_number)
                if play is False:
                    worth_hinting[player_number] = True
            if play is not False:
                player_hand = utils.get_player_hand_by_number(round_info, player_number)
                suit = player_hand[play[1]].real_suit
                rank = player_hand[play[1]].real_rank
                if predicted_board_state[player_number][suit] is rank.value - 1:
                    predicted_board_state[player_number][suit] += 1

            player_number = utils.next_player_number(round_info, player_number)

        player_number = original_player_number
        hinted_plays = {}
        first_time = True

        while player_number is not original_player_number or first_time:
            first_time = False
            hinted_plays[player_number] = {}
            for suit in utils.Suit:
                hinted_plays[player_number][suit] = {}
                for rank in utils.Rank:
                    hinted_plays[player_number][suit][rank] = 0
            player_number = utils.next_player_number(round_info, player_number)

        player_number = utils.next_player_number(round_info, original_player_number)
        for card in original_player_hand:
            if card.revealed_rank is not None and card.revealed_suit is not None and \
                    round_info.board_state[card.real_suit] < card.real_rank.value:
                hinted_plays[original_player_number][card.real_suit][card.real_rank] += 1

        while player_number is not original_player_number:
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
                if card.revealed_suit is None:
                    potential_playable_suits[player_number][card.real_suit].append(card)
                if card.revealed_rank is None:
                    potential_playable_ranks[player_number][card.real_rank].append(card)

            player_number = utils.next_player_number(round_info, player_number)

        max_player_number = 0
        max_potential = -5
        max_hint = 0

        known = {}
        for suit in utils.Suit:
            known[suit] = {}
            for rank in utils.Rank:
                known[suit][rank] = 0

        for card in original_player_hand:
            if card.revealed_rank is not None and card.revealed_suit is not None:
                known[card.revealed_suit][card.revealed_rank] += 1

        for hand in round_info.other_players_hands:
            if original_player_number is not hand.player_number:
                for card in hand:
                    known[card.real_suit][card.real_rank] += 1

        def check_card_potential(card, player, board_state, current_rank=None, pure_info=False):
            player_distance = player - original_player_number - 1
            if player_distance < 0:
                player_distance += round_info.number_of_players

            already_hinted = False
            if card.revealed_suit is None and card.revealed_rank is None:
                for players in hinted_plays:
                    if hinted_plays[players][card.real_suit][card.real_rank] is not 0:
                        already_hinted = True

            card_potential = pow(distance_to_player_multiplier, player_distance) *\
                             pow(lower_rank_multiplier, 5 - card.real_rank.value)

            if (card.revealed_suit is not None or card.revealed_rank is not None) and \
                    card.real_rank.value - board_state[card.real_suit] <= 1 and \
                    self.card_hint_type[player][card.hand_position] is "Play":
                card_potential *= double_hint_multiplier

            if card.real_rank.value <= 4 and card.real_rank.value - board_state[card.real_suit] is 1 and \
                    known[card.real_suit][utils.Rank(card.real_rank.value + 1)] > 0:
                card_potential *= chain_bonus_multiplier

            if already_hinted:
                card_potential += false_tip_penalty

            if pure_info \
                    or (max(round_info.board_state.values()) < card.real_rank.value - 1 and current_rank is None) \
                    or (self.card_hint_type[player][card.hand_position] is "Information"):

                card_potential = information_tip_value * pow(distance_to_player_multiplier, player_distance) * \
                                 pow(lower_rank_multiplier, card.real_rank.value - 1)

                if not already_hinted and \
                        card.real_rank.value - board_state[card.real_suit] is 1 and \
                        self.card_hint_type[player][card.hand_position] is "Information":
                    card_potential = pow(distance_to_player_multiplier, player_distance) * \
                                     pow(lower_rank_multiplier, 5 - card.real_rank.value)

                if card.real_rank.value <= 4 and card.real_rank.value - board_state[card.real_suit] is 1 and \
                        known[card.real_suit][utils.Rank(card.real_rank.value + 1)] > 0:
                    card_potential *= chain_bonus_multiplier

            elif (card.revealed_suit is None and card.revealed_rank is None) and \
                    ((current_rank is None and board_state[card.real_suit] is not card.real_rank.value - 1) or
                     (current_rank is not None and card.real_rank.value is not current_rank)):
                card_potential += false_tip_penalty

            if current_rank is not None and card.real_rank.value is current_rank:
                current_rank += 1

            return card_potential, current_rank

        for player in potential_playable_ranks:
            if debug and round_info.log:
                self.info('{0}'.format(player))

            info_rank = None
            info_suit = None
            player_distance = player - original_player_number - 1
            if player_distance < 0:
                player_distance += round_info.number_of_players

            if player_distance is 0 or not only_next_player:
                if player_distance is 0:
                    play = self.check_for_hinted_play(round_info, player)
                    target_hand = utils.get_player_hand_by_number(round_info, player)
                    if play is not False:
                        if target_hand[play[1]].revealed_rank is None:
                            info_rank = target_hand[play[1]].real_rank
                        if target_hand[play[1]].revealed_suit is None:
                            info_suit = target_hand[play[1]].real_suit
                    else:
                        play = self.check_for_guess_discard(round_info, player)
                        if target_hand[play[1]].revealed_rank is None:
                            info_rank = target_hand[play[1]].real_rank
                        if target_hand[play[1]].revealed_suit is None:
                            info_suit = target_hand[play[1]].real_suit

                for rank in potential_playable_ranks[player]:
                    board_state = deepcopy(predicted_board_state[utils.prev_player_number(round_info, player)])
                    potential = 0
                    for card in potential_playable_ranks[player][rank]:
                        if rank is not info_rank:
                            answer = check_card_potential(card, player, board_state)[0]
                        else:
                            answer = check_card_potential(card, player, board_state, pure_info=True)[0]
                        if answer >= pow(distance_to_player_multiplier, player_distance) * \
                                     pow(lower_rank_multiplier, 5 - card.real_rank.value):
                            board_state[card.real_suit] += 1
                        potential += answer
                    if not worth_hinting[player] and rank is not info_rank:
                        potential *= already_has_play_multiplier
                    if debug and round_info.log:
                        self.info('{0} {1}'.format(rank, potential))
                    if potential > max_potential:
                        max_player_number = player
                        max_potential = potential
                        max_hint = rank

                board_state = deepcopy(predicted_board_state[utils.prev_player_number(round_info, player)])
                for suit in potential_playable_suits[player]:
                    potential = 0
                    current_rank = board_state[suit] + 1
                    for card in potential_playable_suits[player][suit]:
                        if suit is not info_suit:
                            answer = check_card_potential(card, player, board_state, current_rank)
                        else:
                            answer = check_card_potential(card, player, board_state, current_rank, pure_info=True)
                        potential += answer[0]
                        current_rank = answer[1]
                    if not worth_hinting[player] and suit is not info_suit:
                        potential *= already_has_play_multiplier
                    if debug and round_info.log:
                        self.info('{0} {1}'.format(suit, potential))
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

    def check_for_discard_tip(self, round_info, player_number, hint_pass_score=1.8, false_tip_penalty=-10.0,
                              distance_to_player_multiplier=1.01, only_next_player=False):
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
                if card.revealed_suit is None:
                    potential_discardable_suits[player_number][card.real_suit].append(card)
                if card.revealed_rank is None:
                    potential_discardable_ranks[player_number][card.real_rank].append(card)
            player_number = utils.next_player_number(round_info, player_number)

        max_player_number = 0
        max_potential = 0
        max_hint = 0

        def check_card_potential(card, player, hint_type, hint):
            player_distance = player - original_player_number - 1
            if player_distance < 0:
                player_distance += round_info.number_of_players

            card_potential = pow(distance_to_player_multiplier, player_distance)

            card_with_hint = deepcopy(card)
            if hint_type == 'rank':
                card_with_hint.revealed_rank = hint
            else:
                card_with_hint.revealed_suit = hint
            if self.check_card_usefulness(round_info, card_with_hint) is False:
                card_potential += false_tip_penalty

            return card_potential

        for player in potential_discardable_ranks:
            player_distance = player - original_player_number - 1
            if player_distance < 0:
                player_distance += round_info.number_of_players

            if player_distance is 0 or not only_next_player:
                for rank in potential_discardable_ranks[player]:
                    potential = 0
                    for card in potential_discardable_ranks[player][rank]:
                        potential += check_card_potential(card, player, 'rank', rank)
                    if potential > max_potential:
                        max_player_number = player
                        max_potential = potential
                        max_hint = rank

                for suit in potential_discardable_suits[player]:
                    potential = 0
                    for card in potential_discardable_suits[player][suit]:
                        potential += check_card_potential(card, player, 'suit', suit)
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

    def check_for_good_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        play_tip = self.check_for_play_tip(round_info, player_number, self.good_tip[0], self.good_tip[1],
                                           self.good_tip[2], self.good_tip[3], self.good_tip[4], self.good_tip[5],
                                           self.good_tip[6], self.good_tip[7], only_next_player=only_next_player)
        if play_tip is not False:
            return play_tip

        if debug and round_info.log:
            self.info("Discard:")
        discard_tip = self.check_for_discard_tip(round_info, player_number, self.discard_tip[0], self.discard_tip[1],
                                                 self.discard_tip[2], only_next_player=only_next_player)
        return discard_tip

    def check_for_risky_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        return self.check_for_play_tip(round_info, player_number, self.risky_tip[0], self.risky_tip[1],
                                       self.risky_tip[2], self.risky_tip[3], self.risky_tip[4], self.risky_tip[5],
                                       self.risky_tip[6], self.risky_tip[7], only_next_player=only_next_player)

    def check_for_information_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        return self.check_for_play_tip(round_info, player_number, self.information_tip[0], self.information_tip[1],
                                       self.information_tip[2], self.information_tip[3], self.information_tip[4],
                                       self.information_tip[5], self.information_tip[6], self.information_tip[7],
                                       only_next_player=only_next_player)

    def check_for_save_tip(self, round_info, player_number):
        best_player_number = -1
        best_play_priority = False
        best_hint_type = None
        best_hint_rank = 6

        remaining = utils.list_remaining_playable_cards(round_info)
        original_player_number = player_number
        player_number = utils.next_player_number(round_info, utils.next_player_number(round_info, player_number))

        while player_number is not original_player_number and not best_play_priority:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

            play_priority = False
            prev_player = utils.prev_player_number(round_info, player_number)
            play = self.check_for_obvious_play(round_info, prev_player)
            if play is False:
                play = self.check_for_hinted_play(round_info, prev_player)

            if play is not False:
                play_priority = True

            discarded_position = self.check_for_guess_discard(round_info, player_number)[1]
            discarded_card = player_hand[discarded_position]

            if remaining[discarded_card.real_suit][discarded_card.real_rank] is 1 and \
                    max(round_info.board_state.values()) < discarded_card.real_rank.value - 1 and \
                    discarded_card.revealed_rank is None and discarded_card.revealed_suit is None:
                best_player_number = player_number
                best_play_priority = play_priority
                best_hint_type = discarded_card.real_rank

            player_number = utils.next_player_number(round_info, player_number)

        if best_hint_type is None:
            player_number = utils.next_player_number(round_info, utils.next_player_number(round_info, player_number))

            while player_number is not original_player_number and not best_play_priority:
                player_hand = utils.get_player_hand_by_number(round_info, player_number)

                play_priority = False
                prev_player = utils.prev_player_number(round_info, player_number)
                if prev_player is not original_player_number:
                    play = self.check_for_obvious_play(round_info, prev_player)
                    if play is False:
                        play = self.check_for_hinted_play(round_info, prev_player)

                    if play is not False:
                        play_priority = True

                for card in player_hand:
                    if remaining[card.real_suit][card.real_rank] is 1 and \
                            max(round_info.board_state.values()) < card.real_rank.value - 1 and \
                            card.revealed_rank is None and card.revealed_suit is None and \
                            best_hint_rank > card.real_rank.value:
                        best_player_number = player_number
                        best_play_priority = play_priority
                        best_hint_type = card.real_rank
                        best_hint_rank = card.real_rank.value

                player_number = utils.next_player_number(round_info, player_number)

        if best_hint_type is not None:
            return ChoiceDetails(
                Choice.HINT,
                HintDetails(best_player_number, best_hint_type)
            )
        return False

    def info(self, msg):
        self.logger.info(msg)

    def play(self, round_info):
        if round_info.current_turn is 0:
            self.initialize_card_hint_history(round_info)

        if debug and round_info.log:
            self.info("{0}".format(self.card_hint_type))

        self.check_play_history(round_info)

        if debug and round_info.log:
            self.info("{0}".format(self.card_hint_type))

        if round_info.hints is utils.MAX_HINTS:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_good_tip, self.check_for_risky_tip, self.check_for_save_tip,
                            self.check_for_information_tip, self.check_for_obvious_discard, self.check_for_guess_discard]
        elif round_info.hints >= 6:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_good_tip, self.check_for_obvious_discard, self.check_for_risky_tip,
                            self.check_for_save_tip, self.check_for_guess_discard]
        elif round_info.hints >= 3:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_good_tip, self.check_for_obvious_discard, self.check_for_guess_discard]
        else:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_obvious_discard, self.check_for_good_tip, self.check_for_guess_discard]

        for action in action_order:
            if debug and round_info.log:
                self.info('{0}'.format(action))
            decision = functools.partial(action, round_info, round_info.player_turn)()
            if decision is not False:
                return decision
