# -*- coding: utf-8 -*-

from framework import BasePlayer, Choice, ChoiceDetails, utils, HintDetails
import math
from copy import deepcopy
import pickle
from pathlib import Path

debug = False


class ReinforcedFor2(BasePlayer):
    def __init__(self, *args):
        super(ReinforcedFor2, self).__init__(*args)
        self.name = 'ReinforcedFor2'
        self.number_of_players = 2
        self.remaining = {}
        self.known = {}
        self.point_of_uselessness = {}
        self.oldest_card = {}
        self.own_card_states = {}
        self.hint_states = {}
        self.macro_states = {}
        self.load_knowledge()

    def load_knowledge(self):
        root = Path(".")
        folder = root / "players" / "reinforced_for_2_data"
        with open(folder / 'own_card_states.data', 'rb') as file:
            self.own_card_states = pickle.load(file)
        with open(folder / 'hint_states.data', 'rb') as file:
            self.hint_states = pickle.load(file)
        with open(folder / 'macro_states.data', 'rb') as file:
            self.macro_states = pickle.load(file)

    def get_own_card_weights(self, state):
        if state not in self.own_card_states:
            self.own_card_states[state] = [[3, 1, (1, 0), (1, 1), (1, 0)], [3, 1, (1, 0), (1, 1), (1, 0)]]
        return self.own_card_states[state]

    def get_hint_weights(self, state):
        if state not in self.hint_states:
            self.hint_states[state] = [[2, 1, (1, 0), (1, 1)]]
        return self.hint_states[state]

    def get_macro_weights(self, state):
        if state not in self.macro_states:
            self.macro_states[state] = [[3, 1, (1, 0), (1, 1), (1, 0)], [3, 1, (1, 0), (1, 1), (1, 0)],
                                        [3, 1, (1, 0), (1, 1), (1, 0)]]
        return self.macro_states[state]

    def get_chance(self, weights):
        size = len(weights) - 2

        sum_n = 0
        sum_m = 0
        for i in range(-1, -size - 1, -1):
            sum_n += (weights[i][0] * (size + i + 1)) / size
            sum_m += (weights[i][1] * (size + i + 1)) / size

        return sum_m / sum_n

    def initialize_player(self, round_info):
        self.number_of_players = round_info.number_of_players

    def initialize_variables(self, round_info):
        self.remaining = utils.list_remaining_playable_cards(round_info)
        self.point_of_uselessness = {}
        for suit in utils.Suit:
            self.point_of_uselessness[suit] = None
            for rank in utils.Rank:
                if round_info.board_state[suit] < rank.value:
                    if self.point_of_uselessness[suit] is None and self.remaining[suit][rank] == 0:
                        self.point_of_uselessness[suit] = rank

        original_player_number = round_info.player_turn
        player_number = utils.next_player_number(round_info, original_player_number)

        oldest_age = -1
        for card in round_info.player_hand:
            card_age = round_info.current_turn - card.drawn_on_turn
            if card_age > oldest_age:
                oldest_age = card_age
                self.oldest_card[original_player_number] = card.hand_position

        while player_number is not original_player_number:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)
            oldest_age = -1
            for card in player_hand:
                card_age = round_info.current_turn - card.drawn_on_turn
                if card_age > oldest_age:
                    oldest_age = card_age
                    self.oldest_card[player_number] = card.hand_position

            player_number = utils.next_player_number(round_info, player_number)

    def check_card_usefulness(self, round_info, card):
        point_of_uselessness = self.point_of_uselessness
        useless = False

        if card.revealed_rank is None and card.revealed_suit is not None:
            if round_info.board_state[card.revealed_suit] == 5 or \
                    (point_of_uselessness[card.revealed_suit] is not None and
                     round_info.board_state[card.revealed_suit] + 1 is point_of_uselessness[card.revealed_suit].value):
                useless = True

        if card.revealed_rank is not None and card.revealed_suit is None:
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

    def read_own_card(self, round_info, card):
        current_alignment = 0
        future_alignment = 0
        remaining = 2
        if card.revealed_rank is not None and card.revealed_suit is not None:
            if round_info.board_state[card.revealed_suit] is card.revealed_rank.value - 1:
                current_alignment = 1
            elif self.check_card_usefulness(round_info, card) is False:
                future_alignment = 1
            remaining = self.remaining[card.revealed_suit][card.revealed_rank] \
                        - self.known[card.revealed_suit][card.revealed_rank]

        if card.revealed_rank is not None and card.revealed_suit is None:
            for suit in utils.Suit:
                if self.remaining[suit][card.revealed_rank] - self.known[suit][card.revealed_rank] > 0:
                    if round_info.board_state[suit] is card.revealed_rank.value - 1:
                        current_alignment += 1
                    elif self.check_card_usefulness(round_info, card) is False:
                        future_alignment += 1
                    if self.remaining[suit][card.revealed_rank] - self.known[suit][card.revealed_rank] < remaining:
                        remaining = self.remaining[suit][card.revealed_rank] - self.known[suit][card.revealed_rank]

        if card.revealed_rank is None and card.revealed_suit is not None:
            for rank in utils.Rank:
                if self.remaining[card.revealed_suit][rank] - self.known[card.revealed_suit][rank] > 0:
                    if round_info.board_state[card.revealed_suit] is rank.value - 1:
                        current_alignment += 1
                    elif self.check_card_usefulness(round_info, card) is False:
                        future_alignment += 1
                    if self.remaining[card.revealed_suit][rank] - self.known[card.revealed_suit][rank] < remaining:
                        remaining = self.remaining[card.revealed_suit][rank] - self.known[card.revealed_suit][rank]

        if 1 <= current_alignment <= 4:
            current_alignment = 1
        if 1 <= future_alignment:
            future_alignment = 1

        revealed_rank = True
        if card.revealed_rank is None:
            revealed_rank = False
        revealed_suit = True
        if card.revealed_suit is None:
            revealed_suit = False

        hint_size = card.hint_size

        card_age = round_info.current_turn - card.drawn_on_turn
        if card_age > 4:
            card_age = 4

        oldest_card = False
        if card.hand_position is self.oldest_card[card.player_number]:
            oldest_card = True

        hints = round_info.hints
        if 2 <= hints <= 7:
            hints = 2

        state = (current_alignment, future_alignment, revealed_rank, revealed_suit, remaining, hint_size,
                 card_age, oldest_card, hints)

        weights = self.get_own_card_weights(state)
        return state, weights, card.hand_position

    def read_others_hands(self, round_info, player_number):
        original_player_number = player_number

        hints = round_info.hints
        if 2 <= hints <= 7:
            hints = 2

        actions = []

        hinted_plays = {}
        player_hand = round_info.player_hand
        first_time = True

        while player_number is not original_player_number or first_time:
            first_time = False
            hinted_plays[player_number] = {}
            for suit in utils.Suit:
                hinted_plays[player_number][suit] = {}
                for rank in utils.Rank:
                    hinted_plays[player_number][suit][rank] = 0

            player_number = utils.next_player_number(round_info, player_number)

        for card in player_hand:
            if card.revealed_rank is not None and card.revealed_suit is not None and \
                    round_info.board_state[card.real_suit] < card.real_rank.value:
                hinted_plays[original_player_number][card.real_suit][card.real_rank] += 1

        player_number = utils.next_player_number(round_info, original_player_number)

        while player_number is not original_player_number:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)
            for card in player_hand:
                if round_info.board_state[card.real_suit] < card.real_rank.value and \
                        (card.revealed_rank is not None or card.revealed_suit is not None):
                    hinted_plays[player_number][card.real_suit][card.real_rank] += 1

            player_number = utils.next_player_number(round_info, player_number)

        player_number = utils.next_player_number(round_info, original_player_number)
        while player_number is not original_player_number:
            if player_number is not round_info.player_turn:

                player_distance = player_number - original_player_number - 1
                if player_distance < 0:
                    player_distance += round_info.number_of_players

                if player_distance > 0:
                    player_distance = 0

                targets = {}
                for rank in utils.Rank:
                    targets[rank] = []
                for suit in utils.Suit:
                    targets[suit] = []
                player_hand = utils.get_player_hand_by_number(round_info, player_number)

                for card in player_hand:
                    if card.revealed_rank is None:
                        targets[card.real_rank].append(card)
                    if card.revealed_suit is None:
                        targets[card.real_suit].append(card)

                def basic_check(targets, hint, rank=False):
                    current_alignment = 0
                    future_alignment = 0
                    corrected = 0
                    obviously_useless = 0
                    falsely_hinted = 0
                    chain_bonus = 0
                    card_age = 0
                    oldest_card = False
                    last_remaining = 0

                    for card in targets:
                        already_hinted = False
                        if card.revealed_suit is None and card.revealed_rank is None:
                            for players in hinted_plays:
                                if players is not player_number and \
                                        hinted_plays[players][card.real_suit][card.real_rank] != 0:
                                    already_hinted = True

                        card_with_hint = deepcopy(card)
                        if rank:
                            card_with_hint.revealed_rank = hint
                        else:
                            card_with_hint.revealed_suit = hint

                        if self.check_card_usefulness(round_info, card_with_hint) is not False \
                                and self.check_card_usefulness(round_info, card) is False:
                            obviously_useless += 1

                        if rank:
                            card_with_hint.revealed_suit = card.real_suit
                        else:
                            card_with_hint.revealed_rank = card.real_rank

                        if round_info.board_state[card.real_suit] is card.real_rank.value - 1:
                            if self.remaining[card.real_suit][card.real_rank] == 1 \
                                    and ((rank and card.revealed_suit is None)
                                         or (not rank and card.revealed_rank is None)):
                                last_remaining += 1

                            if card.revealed_rank is not None or card.revealed_suit is not None and \
                                    round_info.current_turn - card.drawn_on_turn > 2:
                                corrected += 1

                            if already_hinted:
                                falsely_hinted += 1

                            else:
                                current_alignment += 1
                                chain = 1
                                if card.real_rank.value + chain <= 5 and \
                                        self.known[card.real_suit][utils.Rank(card.real_rank.value + chain)] > 0:
                                    chain += 1
                                    chain_bonus += 1

                        elif self.check_card_usefulness(round_info, card_with_hint) is False:
                            if self.remaining[card.real_suit][card.real_rank] == 1 \
                                    and ((rank and card.revealed_suit is None)
                                         or (not rank and card.revealed_rank is None)):
                                last_remaining += 1

                            if card.revealed_rank is not None or card.revealed_suit is not None:
                                corrected += 1

                            future_alignment += 1

                        if round_info.board_state[card.real_suit] is not card.real_rank.value - 1 \
                                and ((rank and card.revealed_suit is None)
                                     or (not rank and card.revealed_rank is None)):
                            falsely_hinted += 1

                        if round_info.current_turn - card.drawn_on_turn > card_age:
                            card_age = round_info.current_turn - card.drawn_on_turn

                        if card.hand_position is self.oldest_card[card.player_number]:
                            oldest_card = True

                    if card_age > 3:
                        card_age = 3

                    if current_alignment > 2:
                        current_alignment = 2

                    if future_alignment > 2:
                        future_alignment = 2

                    if obviously_useless > 2:
                        obviously_useless = 2

                    if corrected > 2:
                        corrected = 2

                    if falsely_hinted > 2:
                        falsely_hinted = 2

                    chain_bonus = math.ceil(chain_bonus / 2)
                    if chain_bonus > 2:
                        chain_bonus = 2

                    if last_remaining > 1:
                        last_remaining = 1

                    state = (rank, current_alignment, future_alignment, obviously_useless, corrected, falsely_hinted,
                             chain_bonus, last_remaining, card_age, oldest_card, player_distance)

                    weights = self.get_hint_weights(state)
                    return state, weights, player_number, hint

                for rank in utils.Rank:
                    if len(targets[rank]) > 0:
                        actions.append(basic_check(targets[rank], rank, True))

                for suit in utils.Suit:
                    if len(targets[suit]) > 0:
                        actions.append(basic_check(targets[suit], suit, False))

            player_number = utils.next_player_number(round_info, player_number)

        return actions

    def decide_macro_action(self, round_info, play_actions, hint_actions):
        if round_info.current_deck_size == 0:
            deck_remains = False
        else:
            deck_remains = True

        hints = round_info.hints

        lives = round_info.lives
        if lives > 1:
            lives = 2

        play_quality = 0
        discard_quality = 0
        hint_quality = 0

        for play in play_actions:
            if self.get_chance(play[1][0]) > play_quality:
                play_quality = self.get_chance(play[1][0])
            if self.get_chance(play[1][1]) > discard_quality:
                discard_quality = self.get_chance(play[1][1])

        for hint in hint_actions:
            if self.get_chance(hint[1][0]) > hint_quality:
                hint_quality = self.get_chance(hint[1][0])

        def quality_to_heuristic(quality):
            if quality <= 0.1:
                quality = 0
            elif quality <= 0.3:
                quality = 1
            elif quality <= 0.5:
                quality = 2
            elif quality <= 0.7:
                quality = 3
            elif quality <= 0.9:
                quality = 4
            else:
                quality = 5
            return quality

        play_quality = quality_to_heuristic(play_quality)
        discard_quality = quality_to_heuristic(discard_quality)
        hint_quality = quality_to_heuristic(hint_quality)

        state = (hints, lives, deck_remains, play_quality, discard_quality, hint_quality)
        weights = self.get_macro_weights(state)
        return state, weights

    def read_board(self, round_info, player_number):
        self.known = utils.list_others_cards(round_info, player_number)
        if player_number is round_info.player_turn:
            player_hand = round_info.player_hand
        else:
            player_hand = utils.get_player_hand_by_number(round_info, player_number)

        play_actions = []
        for card in player_hand:
            play_actions.append(self.read_own_card(round_info, card))

        hint_actions = []
        if round_info.hints > 0:
            hint_actions = self.read_others_hands(round_info, player_number)

        used_actions = []
        used_hints = []

        max_of_weights = -1
        used_play = None

        for play in play_actions:
            if round_info.log and debug:
                self.info("{0} {1} {2} {3}".format(play[0], play[1][0][0],
                                                   self.get_chance(play[1][0]), play[2]))

            sum_of_weights = self.get_chance(play[1][0])

            if sum_of_weights > max_of_weights:
                max_of_weights = sum_of_weights
                used_play = play

        used_actions.append(used_play)

        max_of_weights = -1
        used_play = None

        for play in play_actions:
            if round_info.log and debug:
                self.info("{0} {1} {2} {3}".format(play[0], play[1][1][0],
                                                   self.get_chance(play[1][1]), play[2]))

            sum_of_weights = self.get_chance(play[1][1])

            if sum_of_weights >= max_of_weights:
                max_of_weights = sum_of_weights
                used_play = play

        used_actions.append(used_play)

        if round_info.hints > 0:
            max_of_weights = -1
            used_hint = None

            for hint in hint_actions:
                if round_info.log and debug:
                    self.info("{0} {1} {2} {3} {4}".format(hint[0], hint[1][0][0],
                                                           self.get_chance(hint[1][0]),
                                                           hint[2], hint[3]))

                sum_of_weights = self.get_chance(hint[1][0])

                if sum_of_weights > max_of_weights:
                    max_of_weights = sum_of_weights
                    used_hint = hint

            used_hints.append(used_hint)

        if len(used_hints) > 0 and used_hints[0] is None:
            used_hints = []

        macro_weights = self.decide_macro_action(round_info, used_actions, used_hints)

        macro_max = 0
        macro_action = "Discard"

        sum_of_weights = self.get_chance(macro_weights[1][0])

        if macro_max < sum_of_weights:
            macro_max = sum_of_weights
            macro_action = "Play"

        sum_of_weights = self.get_chance(macro_weights[1][1])

        if macro_max < sum_of_weights:
            macro_max = sum_of_weights
            macro_action = "Discard"

        sum_of_weights = self.get_chance(macro_weights[1][2])

        if macro_max < sum_of_weights and round_info.hints > 0 and len(used_hints) > 0:
            macro_action = "Hint"

        used_state = None
        action = None

        if macro_action == "Play":
            used_state = used_actions[0]
            action = ChoiceDetails(
                Choice.PLAY,
                used_actions[0][2]
            )

        if macro_action == "Discard":
            used_state = used_actions[1]
            action = ChoiceDetails(
                Choice.DISCARD,
                used_actions[1][2]
            )

        if macro_action == "Hint":
            used_state = used_hints[0]
            action = ChoiceDetails(
                Choice.HINT,
                HintDetails(used_hints[0][2], used_hints[0][3])
            )

        if round_info.log and debug:
            self.info("{0}".format(macro_action))
            self.info("{0} {1} {2}".format(used_state[0], used_state[1][0][0],
                                           self.get_chance(used_state[1][0])))
            self.info("{0} {1} {2}".format(macro_weights[0], macro_weights[1][0][0],
                                           self.get_chance(macro_weights[1][0])))

        return action

    def info(self, msg):
        self.logger.info(msg)

    def play(self, round_info):
        if round_info.current_turn == 0:
            self.initialize_player(round_info)
        self.initialize_variables(round_info)
        return self.read_board(round_info, round_info.player_turn)
