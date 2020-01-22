# -*- coding: utf-8 -*-

from copy import deepcopy
from enum import Enum, auto


class Rank(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    def __str__(self):
        return str(self.value)


class Suit(Enum):
    BLUE = auto()
    GREEN = auto()
    RED = auto()
    WHITE = auto()
    YELLOW = auto()

    def __str__(self):
        return self.name.capitalize()


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
        self.drawn_on_turn = None
        self.hint_size = 0
        self.hint_states = []

    def __eq__(self, other):
        if self.real_rank is None or self.real_suit is None:
            return False

        if other.real_rank is None or other.real_suit is None:
            return False

        return self.real_rank is other.real_rank and self.real_suit is other.real_suit

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

    def reveal_info_from_hint(self, hint, reveal_size, state=None):
        revealed = False
        if self.real_rank == hint and self.revealed_rank is None:
            self.revealed_rank = self.real_rank
            revealed = True
        if self.real_suit == hint and self.revealed_suit is None:
            self.revealed_suit = self.real_suit
            revealed = True

        if revealed:
            self.hint_size = reveal_size
        if self.revealed_suit is not None and self.revealed_rank is not None:
            self.hint_size = 0

        if state is not None:
            self.hint_states.append(state)

    def is_playable(self, round_info):
        board_state = round_info.board_state
        if self.revealed_suit is None or self.revealed_rank is None:
            if self.real_suit is None or self.real_rank is None:
                return False
            else:
                return board_state[self.real_suit] + 1 == self.real_rank.value
        else:
            return board_state[self.revealed_suit] + 1 == self.revealed_rank.value
