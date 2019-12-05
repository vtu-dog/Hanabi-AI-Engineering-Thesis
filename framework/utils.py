# -*- coding: utf-8 -*-

from collections import namedtuple
from enum import Enum, auto

from .card import Rank, Suit


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
    return next(iter(list(filter(fun, lst))))


def prev_player_number(round_info, player_number):
    if player_number is 0:
        return round_info.number_of_players - 1
    else:
        return player_number - 1


def next_player_number(round_info, player_number):
    if round_info.number_of_players - 1 is player_number:
        return 0
    else:
        return player_number + 1


def get_player_hand_by_number(round_info, number):
    return first_occurrence(
        lambda p: p.player_number == number,
        round_info.other_players_hands
    )


def next_player_hand(round_info, player_number):
    return get_player_hand_by_number(
        round_info,
        next_player_number(round_info, player_number)
    )


def list_all_known_cards(round_info):
    known = {}
    unknown_rank = {}
    unknown_suit = {}
    for suit in Suit:
        known[suit] = {}
        unknown_rank[suit] = 0
        for rank in Rank:
            unknown_suit[rank] = 0
            known[suit][rank] = 0

    player_hand = round_info.player_hand
    for card in player_hand:
        if card.revealed_rank is not None and card.revealed_suit is not None:
            known[card.revealed_suit][card.revealed_rank] += 1
        elif card.revealed_rank is not None:
            unknown_suit[card.revealed_rank] += 1
        elif card.revealed_suit is not None:
            unknown_rank[card.revealed_suit] += 1

    for player_hand in round_info.other_players_hands:
        for card in player_hand:
            known[card.real_suit][card.real_rank] += 1

    for card in round_info.discarded:
        known[card.real_suit][card.real_rank] += 1

    for card in round_info.played:
        known[card.real_suit][card.real_rank] += 1

    return known, unknown_suit, unknown_rank


def list_remaining_playable_cards(round_info):
    remaining = {}
    for suit in Suit:
        remaining[suit] = {}
        remaining[suit][Rank.ONE] = 3
        remaining[suit][Rank.TWO] = 2
        remaining[suit][Rank.THREE] = 2
        remaining[suit][Rank.FOUR] = 2
        remaining[suit][Rank.FIVE] = 1

    for card in round_info.discarded:
        remaining[card.real_suit][card.real_rank] -= 1
    for card in round_info.played:
        remaining[card.real_suit][card.real_rank] -= 1

    return remaining


def list_discarded_cards(round_info):
    discarded = {}
    for suit in Suit:
        discarded[suit] = {}
        for rank in Rank:
            discarded[suit][rank] = 0

    for card in round_info.discarded:
        discarded[card.real_suit][card.real_rank] += 1

    return discarded
