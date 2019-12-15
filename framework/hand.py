# -*- coding: utf-8 -*-


class Hand:
    def __init__(self, player_number):
        self.cards = []
        self.player_number = player_number

    def __contains__(self, card):
        return card in self.cards

    def __iter__(self):
        return iter(self.cards)

    def __getitem__(self, index):
        return self.cards[index]

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return ', '.join([str(card) for card in self.cards])

    def __fix_cards(self):
        for pos, card in enumerate(self.cards):
            card.hand_position = pos
            card.player_number = self.player_number

    def current_knowledge(self):
        return ', '.join([card.current_knowledge() for card in self.cards])

    def add(self, card):
        card.player_number = self.player_number
        self.cards.append(card)
        self.__fix_cards()

    def discard(self, hand_position):
        self.cards.pop(hand_position)
        self.__fix_cards()

    def replace(self, card, hand_position):
        card.hand_position = hand_position
        card.player_number = self.player_number
        self.cards[hand_position] = card

    def playable_cards(self, board_state):
        res = []
        for card in self:
            if card.is_playable(board_state.board_state):
                res.append(card)

        return res
