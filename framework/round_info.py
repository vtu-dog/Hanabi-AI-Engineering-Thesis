# -*- coding: utf-8 -*-

from copy import deepcopy
from .utils import first_occurrence


class RoundInfo:
    def __init__(self, round):
        self.__full_info_player_hand = deepcopy(round.current_player_hand)
        self.player_hand = self.hide_hand(round.current_player_hand)
        self.other_players_hands = round.other_players_hands
        self.current_turn = round.current_turn
        self.player_turn = round.player_turn
        self.hints = round.hints
        self.lives = round.lives
        self.score = round.score
        self.board_state = round.board_state
        self.played = round.played
        self.discarded = round.discarded
        self.current_deck_size = len(round.deck)

    def hide_hand(self, hand):
        temp_hand = deepcopy(hand)
        for card in temp_hand:
            card.hide_info()
        return temp_hand

    def true_hand_info(self):
        return self.__full_info_player_hand
