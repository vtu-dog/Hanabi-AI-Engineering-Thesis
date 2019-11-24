# -*- coding: utf-8 -*-

from copy import deepcopy
from enum import Enum, auto


class Rank(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class Suit(Enum):
    BLUE = auto()
    GREEN = auto()
    RED = auto()
    WHITE = auto()
    YELLOW = auto()


class Card:
    def __init__(self, rank, suit, position=None):
        self.real_rank = rank
        self.real_suit = suit
        self.hand_position = position
        self.player_number = None
        self.revealed_rank = None
        self.revealed_suit = None
        self.misplayed = False
        self.discarded = False
        self.played_on_turn = None

    def __eq__(self, other):
        pass

    def __str__(self):
        if self.real_rank is None and self.real_suit is None:
            return '???'

        if self.real_rank is None:
            rank = '???'
        else:
            rank = str(self.real_rank.value)

        if self.real_suit is None:
            suit = '???'
        else:
            suit = self.real_suit.name.capitalize()

        return '{0} {1}'.format(suit, rank)

    def current_knowledge(self):
        card_copy = deepcopy(self)
        card_copy.hide_info()
        return str(card_copy)

    def hide_info(self):
        self.real_rank = self.revealed_rank
        self.real_suit = self.revealed_suit

    def reveal_info_from_hint(self, hint):
        if self.real_rank == hint:
            self.revealed_rank = self.real_rank
        if self.real_suit == hint:
            self.revealed_suit = self.real_suit

    def is_playable(self, board_state):
        if self.real_suit is None or self.real_rank is None:
            return False
        else:
            return board_state[self.real_suit] + 1 == self.real_rank.value
