# -*- coding: utf-8 -*-

from .card import Rank, Suit, Card
from .hand import Hand
from .learning_state import LearningState
from .round_info import RoundInfo
from .utils import *

from copy import deepcopy
from random import shuffle


class Game:
    def __init__(self, players, logger=None, log=False, learning_state=None):
        self.logger = logger
        self.log = log

        self.learning_state = learning_state

        self.players = players
        self.number_of_players = len(players)
        assert(MIN_PLAYERS <= self.number_of_players <= MAX_PLAYERS)

        for player_number, player in enumerate(self.players):
            player.inject_info(
                player_number,
                self.logger,
                self.learning_state,
                ' #{0}'.format(str(player_number + 1))
            )

        self.hints = MAX_HINTS
        self.lives = LIVES
        self.score = 0

        self.deck = []
        self.all_cards = []
        self.board_state = {suit: 0 for suit in Suit}
        self.deck_size = 0

        self.played = []
        self.discarded = []
        self.history = []

        self.hands = []
        self.hands_history = []

        self.current_turn = 0
        self.player_turn = 0

        self.current_player_hand = None
        self.other_players_hands = None
        self.game_over_timer = None
        self.game_over = False
        self.game_ended_by_timeout = False

        self.__prepare_game()

    def info(self, msg):
        if self.log:
            self.logger.info(msg)

    def __draw_card(self):
        if self.deck_size != 0:
            self.deck_size -= 1
            if self.log and self.deck_size == 0:
                msg1 = 'Last card has been drawn,'
                msg2 = 'each player gets one more turn'
                self.info('{0} {1}'.format(msg1, msg2))
            return self.deck.pop()
        else:
            return None

    def __prepare_game(self):
        for rank in RANKS:
            for suit in Suit:
                self.deck.append(Card(rank, suit))

        self.all_cards = self.deck[:]
        self.deck_size = len(self.deck)
        shuffle(self.deck)

        if self.number_of_players <= 3:
            hand_size = 5
        else:
            hand_size = 4

        for player_number in range(self.number_of_players):
            player_hand = Hand(player_number)
            for hand_position in range(hand_size):
                card = self.__draw_card()
                card.hand_position = hand_position
                card.drawn_on_turn = self.current_turn
                player_hand.add(card)
            self.hands.append(player_hand)

        self.hands_history.append(self.hands)

        self.info('Preparing game... Done.\n')
        self.info('Hands have been dealt as follows:')

        if self.log:
            for hand in self.hands:
                self.info('{0}: {1}'.format(
                    self.players[hand.player_number].name,
                    hand)
                )

        self.info('\nBeginning game...\n')

    def __is_inbounds(self, lst, index):
        return 0 <= index < len(lst)

    def __is_legal(self, move):
        if type(move) is not ChoiceDetails:
            print('wrong move: ' + str(move))
        assert(type(move) is ChoiceDetails)
        if type(move.choice) is not Choice:
            print('wrong choice from move: ' + str(move))
        assert(type(move.choice) is Choice)

        choice = move.choice

        if choice is Choice.PLAY or choice is Choice.DISCARD:
            hand_position = move.details
            return self.__is_inbounds(self.current_player_hand, hand_position)

        elif choice is Choice.HINT:
            assert(type(move.details) is HintDetails)
            if self.hints > 0:
                player_number, hint = move.details
                assert(type(hint) is Rank or type(hint) is Suit)

                target_player_hand = get_player_hand_by_number(
                    self,
                    player_number
                )

                return target_player_hand is not None

        return False

    def __print_player_knowledge(self, number):
        if self.log:
            player = self.players[number]
            hand = get_player_hand_by_number(self, number).current_knowledge()
            self.info('Current knowledge of {0}: {1}'.format(player, hand))

    def __print_current_hands(self):
        if self.log:
            self.info('Current player hands and their knowledge:')
            for hand in self.hands:
                self.info('{0}: {1}'.format(
                    self.players[hand.player_number].name,
                    hand)
                )
                self.info('{0}: {1}'.format(
                    self.players[hand.player_number].name,
                    hand.current_knowledge())
                )

    def __print_current_board(self):
        if self.log:
            self.info('Current board situation:')
            for suit in self.board_state:
                self.info('{0}: {1}'.format(
                    suit,
                    self.board_state[suit])
                )

    def make_move(self):
        assert(self.lives != 0)
        assert(self.hints >= 0)

        if self.log and self.player_turn == 0:
            self.info('')
            self.__print_current_hands()
            self.__print_current_board()
            self.info('')

        player_hands = deepcopy(self.hands)
        self.current_player_hand = player_hands[self.player_turn]
        self.other_players_hands = [
            hand for hand in player_hands
            if hand.player_number != self.player_turn
        ]

        move = self.players[self.player_turn].play(RoundInfo(self))
        learning_player = self.players[self.player_turn].learning

        assert(self.__is_legal(move))

        choice = move.choice

        if choice is Choice.PLAY:
            hand_position = move.details
            card = self.current_player_hand[hand_position]

            card.played_on_turn = self.current_turn
            card.hand_position = None

            if card.is_playable(self):
                self.history.append(PlayDetails(
                    choice, hand_position, card, self.deck_size))
                self.board_state[card.real_suit] += 1

                if card.real_rank is Rank.FIVE:
                    self.hints = min(self.hints + 1, MAX_HINTS)

                self.score += 1
                self.played.append(card)

                if learning_player:
                    self.players[self.player_turn].analyze_turn(
                        'Correct Play', card, RoundInfo(self))

                self.info(
                    '{0} correctly played {1}'.format(
                        self.players[self.player_turn],
                        card
                    )
                )
                info_msg = 'Played {0}'.format(card)

            else:
                card.misplayed = True
                self.history.append(PlayDetails(
                    choice, hand_position, card, self.deck_size))

                self.lives -= 1
                self.discarded.append(card)

                if learning_player:
                    self.players[self.player_turn].analyze_turn(
                        'Wrong Play', card, RoundInfo(self))

                self.info(
                    '{0} misplayed {1}, {2} lives remaining'.format(
                        self.players[self.player_turn],
                        card,
                        self.lives
                    )
                )
                info_msg = 'Misplayed {0}'.format(card)

        if choice is Choice.DISCARD:
            hand_position = move.details
            card = self.current_player_hand[hand_position]

            card.played_on_turn = self.current_turn
            card.discarded = True
            card.hand_position = None

            self.history.append(PlayDetails(
                choice, hand_position, card, self.deck_size))
            self.discarded.append(card)

            if learning_player:
                self.players[self.player_turn].analyze_turn(
                    'Discard', card, RoundInfo(self))

            self.hints = min(self.hints + 1, MAX_HINTS)

            self.info(
                '{0} discarded {1}, the number of hints is currently {2}'.format(
                    self.players[self.player_turn],
                    card,
                    self.hints
                )
            )
            info_msg = 'Discarded {0}'.format(card)

        if choice is Choice.HINT:
            player_number, hint = move.details

            hand = get_player_hand_by_number(self, player_number)
            reveal_size = 0
            for card in hand:
                if card.real_rank is hint and card.revealed_rank is not hint:
                    reveal_size += 1
                if card.real_suit is hint and card.revealed_suit is not hint:
                    reveal_size += 1

            state = None
            if learning_player:
                state = self.learning_state.get_last_hint_state()

            for card in hand:
                card.reveal_info_from_hint(hint, reveal_size, state)

            self.history.append(PlayDetails(
                choice, move.details[0], move.details[1], self.deck_size))

            if learning_player:
                self.players[self.player_turn].analyze_turn(
                    'Hint', (player_number, hint), RoundInfo(self))

            self.hints -= 1
            self.info(
                '{0} hinted {1} to {2}, {3} hints remaining'.format(
                    self.players[self.player_turn],
                    hint,
                    self.players[player_number],
                    self.hints
                )
            )
            info_msg = 'Hinted {0} to P{1}'.format(
                hint, player_number + 1)

        if self.lives == 0 or self.score == MAX_SCORE:
            self.game_over = True

        skip_timer = False

        if choice is not Choice.HINT:
            new_card = self.__draw_card()

            if len(self.deck) == 0:
                if self.game_over_timer is None:
                    self.game_over_timer = self.player_turn
                    skip_timer = True

            if new_card is None:
                self.current_player_hand.discard(hand_position)

            else:
                new_card.drawn_on_turn = self.current_turn
                self.current_player_hand.replace(new_card, hand_position)

        new_hands = [self.current_player_hand] + self.other_players_hands
        new_hands.sort(key=lambda h: h.player_number)
        self.hands_history.append(new_hands)
        self.hands = new_hands

        if choice is Choice.HINT:
            self.__print_player_knowledge(player_number)

        if self.game_over_timer is self.player_turn and skip_timer is False:
            self.game_over = True
            self.game_ended_by_timeout = True

        if self.game_over:
            if learning_player:
                self.players[self.player_turn].analyze_game(
                    RoundInfo(self), self.score)

            if self.score is MAX_SCORE:
                self.info('\nPerfect victory!')
            elif self.game_ended_by_timeout:
                self.info(
                    '\nNo cards left in the deck! Total points: {0}'.format(self.score))
            else:
                self.info(
                    '\nGame over! Total points: {0}'.format(self.score))

        self.player_turn = next_player_number(self, self.player_turn)

        if self.player_turn == 0:
            self.current_turn += 1

        return info_msg

    def is_game_over(self):
        return self.game_over
