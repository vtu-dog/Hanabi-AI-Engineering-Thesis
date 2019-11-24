# -*- coding: utf-8 -*-

from collections import namedtuple
from enum import Enum, auto

from .card import Rank


MIN_PLAYERS = 2
MAX_PLAYERS = 5

MAX_SCORE = 25
MAX_HINTS = 8
LIVES = 3

RANKS = [
    Rank.ONE, Rank.ONE, Rank.ONE,
    Rank.TWO, Rank.TWO,
    Rank.THREE, Rank.THREE,
    Rank.FOUR, Rank.FOUR,
    Rank.FIVE
]


class Choice(Enum):
    PLAY = auto()
    DISCARD = auto()
    HINT = auto()


ChoiceDetails = namedtuple('ChoiceDetails', ['choice', 'details'])
HintDetails = namedtuple('HintDetails', ['player_number', 'hint'])


def first_occurrence(fun, lst):
    return next(iter(list(filter(fun, lst))), None)
