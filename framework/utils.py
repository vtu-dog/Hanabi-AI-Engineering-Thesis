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
PlayDetails = namedtuple('PlayDetails', ['choice', 'details'])


def first_occurrence(fun, lst):
    return next(iter(list(filter(fun, lst))), None)


def prev_player_number(round_info):
    if round_info.player_turn is 0:
        return round_info.number_of_players - 1
    else:
        return round_info.player_turn - 1


def next_player_number(round_info):
    if round_info.number_of_players - 1 is round_info.player_turn:
        return 0
    else:
        return round_info.player_turn + 1


def get_player_hand_by_number(round_info, number):
    return first_occurrence(
        lambda p: p.player_number == number,
        round_info.other_players_hands
    )


def next_player_hand(round_info):
    return get_player_hand_by_number(
        round_info,
        next_player_number(round_info)
    )
