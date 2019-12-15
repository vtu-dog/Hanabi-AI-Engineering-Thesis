#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from framework import utils, game, card, base_player
from players import *

subclasses = sorted([cls.__name__ for cls in BasePlayer.__subclasses__()])

import tkinter as tk

bg = '#%02x%02x%02x' % ((33, 33, 33))

root = tk.Tk()
root.resizable(False, False)
root.title("Hanabi launcher")
root.configure(background=bg)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

frame1 = tk.Frame(root, background=bg)
frame2 = tk.Frame(root, background=bg)
frame3 = tk.Frame(root, background=bg)

frame1.grid(row=0, column=0)
frame2.grid(row=1, column=0)
frame3.grid(row=2, column=0)

tk.Label(
    frame1,
    text="Choose the AI to play with:",
    background=bg,
    foreground='white',
).grid(row=1, column=1, padx=40, pady=(20, 15))

mainframe = tk.Frame(frame2, background=bg)
mainframe.grid(column=0, row=0, sticky='swne')

choice_boxes = [tk.StringVar(root) for _ in range(4)]

choice_boxes[0].set(subclasses[0])
for elem in choice_boxes[1:]:
    elem.set('None')

choices = ['None'] + subclasses

popups = [
    tk.OptionMenu(mainframe, c, *choices)
    for c in choice_boxes[1:]
]
popups = [tk.OptionMenu(mainframe, choice_boxes[0], *choices[1:])] + popups

for elem in popups:
    elem.configure(background=bg)

positions = [(1, 1, 2, 1), (1, 2, 2, 2), (3, 1, 4, 1), (3, 2, 4, 2)]

for i, elem in enumerate(popups, 2):
    pos = positions[i - 2]
    tk.Label(
        mainframe,
        text="Player {0}".format(i),
        background=bg,
        foreground='white'
    ).grid(row=pos[0], column=pos[1], padx=5)
    elem.grid(row=pos[2], column=pos[3], padx=5, pady=(0, 10))


def quit():
    root.destroy()
    sys.exit(0)


def confirm():
    root.destroy()


button_row = tk.Frame(frame3, background=bg)
button_row.grid(column=0, row=0, sticky='swne')

quit_button = tk.Button(frame3, text="Quit", command=quit,
                        highlightbackground=bg)
ok_button = tk.Button(frame3, text="Confirm", command=confirm,
                      highlightbackground=bg)

quit_button.grid(row=1, column=1, padx=8, pady=(20, 20))
ok_button.grid(row=1, column=2, padx=8, pady=(20, 20))

root.protocol("WM_DELETE_WINDOW", quit)
root.mainloop()


from kivy.config import Config
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform


class HumanPlayer(base_player.BasePlayer):
    def __init__(self, *args):
        super(HumanPlayer, self).__init__(*args)
        self.name = 'Player'

    def play(self, round_info):
        return hanabi_game.player_choice


class GameInfo(BoxLayout):
    lives = ObjectProperty(None)
    hints = ObjectProperty(None)
    cards_left = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GameInfo, self).__init__(**kwargs)

    def update(self, game):
        self.lives.text = 'Lives: {0}'.format(game.lives)
        self.hints.text = 'Hints: {0}'.format(game.hints)
        self.cards_left.text = 'Cards left in the deck: {0}'.format(
            len(game.deck))


class GameButtons(GridLayout):
    play_toggle = ObjectProperty(None)
    discard_toggle = ObjectProperty(None)
    hint_rank_toggle = ObjectProperty(None)
    hint_suit_toggle = ObjectProperty(None)
    next_turn_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GameButtons, self).__init__(**kwargs)
        self.alter = False
        Clock.schedule_once(self.bind_buttons, 0)

    def bind_buttons(self, *args):
        self.play_toggle.state = 'down'
        self.play_toggle.bind(state=self.play)
        self.discard_toggle.bind(state=self.discard)
        self.hint_rank_toggle.bind(state=self.hint_rank)
        self.hint_suit_toggle.bind(state=self.hint_suit)
        self.next_turn_button.bind(state=self.next_turn)

    def play(self, instance, value):
        if self.alter:
            self.alter = False
            return
        elif value == 'down':
            self.discard_toggle.state = 'normal'
            self.hint_rank_toggle.state = 'normal'
            self.hint_suit_toggle.state = 'normal'
        else:
            if self.discard_toggle.state == 'normal' \
                    and self.hint_rank_toggle.state == 'normal' \
                    and self.hint_suit_toggle.state == 'normal':
                self.alter = True
                self.play_toggle.state = 'down'

        hanabi_game.play_discard_toggled()

    def discard(self, instance, value):
        if self.alter:
            self.alter = False
            return
        elif value == 'down':
            self.play_toggle.state = 'normal'
            self.hint_rank_toggle.state = 'normal'
            self.hint_suit_toggle.state = 'normal'
        else:
            if self.play_toggle.state == 'normal' \
                    and self.hint_rank_toggle.state == 'normal' \
                    and self.hint_suit_toggle.state == 'normal':
                self.alter = True
                self.discard_toggle.state = 'down'

        hanabi_game.play_discard_toggled()

    def hint_rank(self, instance, value):
        if self.alter:
            self.alter = False
            return
        elif value == 'down':
            self.play_toggle.state = 'normal'
            self.discard_toggle.state = 'normal'
            self.hint_suit_toggle.state = 'normal'
        else:
            if self.play_toggle.state == 'normal' \
                    and self.discard_toggle.state == 'normal' \
                    and self.hint_suit_toggle.state == 'normal':
                self.alter = True
                self.hint_rank_toggle.state = 'down'

        hanabi_game.hint_toggled()

    def hint_suit(self, instance, value):
        if self.alter:
            self.alter = False
            return
        elif value == 'down':
            self.play_toggle.state = 'normal'
            self.discard_toggle.state = 'normal'
            self.hint_rank_toggle.state = 'normal'
        else:
            if self.play_toggle.state == 'normal' \
                    and self.discard_toggle.state == 'normal' \
                    and self.hint_rank_toggle.state == 'normal':
                self.alter = True
                self.hint_suit_toggle.state = 'down'

        hanabi_game.hint_toggled()

    def next_turn(self, instance, value):
        if value == 'normal':
            hanabi_game.update()


class Card(Image):
    def __init__(self, card, full_info, is_tintable, **kwargs):
        super(Card, self).__init__(**kwargs)
        self.size_hint = 1, 1

        self.first_update_done = False
        self.full_info = full_info
        self.is_tintable = is_tintable
        self.is_tinted = False
        self.dead = False

        self.set_card(card)
        self.update()

    def set_card(self, card):
        self.card = card
        self.hand_position = card.hand_position
        self.player_number = card.player_number
        self.real_rank = card.real_rank
        self.real_suit = card.real_suit
        self.revealed_rank = card.revealed_rank
        self.revealed_suit = card.revealed_suit

    def tint(self, set_card=False):
        if self.dead:
            return

        if self.is_tintable and set_card is False:
            self.is_tinted = True
            self.opacity = 0.6

    def untint(self, set_card=False):
        if self.dead:
            return

        if set_card is True:
            global hanabi_game
            hanabi_game.tint_all()
            hanabi_game.player_choice = self

        self.is_tinted = False
        self.opacity = 1

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.is_tinted:
                self.untint(set_card=True)
            else:
                self.tint(set_card=True)

    def update(self, board=False):
        if board:
            rank = hanabi_game.game.board_state[self.real_suit]
            if rank == 0:
                self.real_rank = None
                self.revealed_rank = None
            else:
                self.real_rank = card.Rank(rank)
                self.revealed_rank = card.Rank(rank)
        elif self.first_update_done:
            try:
                self.set_card(
                    hanabi_game.game.hands[self.player_number][self.hand_position]
                )
            except IndexError:
                self.opacity = 0
                self.dead = True
                return

        if self.full_info:
            rank = self.real_rank
            suit = self.real_suit
        else:
            rank = self.revealed_rank
            suit = self.revealed_suit

        if rank is None:
            if hasattr(self.card, 'is_on_board'):
                rank_str = '0'
            else:
                rank_str = ''
        else:
            rank_str = str(rank.value)

        if suit is None:
            suit_str = 'colorless'
        else:
            suit_str = str(suit).lower()

        self.source = "assets/{0}{1}.png".format(suit_str, rank_str)
        self.first_update_done = True


class Hand(BoxLayout):
    def __init__(self, hand, full_info, is_tintable, **kwargs):
        super(Hand, self).__init__(**kwargs)
        self.box = BoxLayout(orientation='horizontal')
        self.box.spacing = 5
        self.full_info = full_info
        self.cards = []

        self.player_number = hand[0].player_number

        for new_card in hand:
            self.cards.append(Card(new_card, full_info, is_tintable))

        if self.full_info is True:
            self.label = Label(
                text='Full hand',
                size_hint=(1, 0.25),
                padding=(10, 10)
            )
            self.label.size = self.label.texture_size
        else:
            self.label = Label(
                text='Revealed hand',
                size_hint=(1, 0.25),
                padding=(10, 100)
            )
            self.label.size = self.label.texture_size

        for new_card in self.cards:
            self.box.add_widget(new_card)

        self.add_widget(self.label)
        self.add_widget(self.box)

    def update(self, board=False):
        for card in self.cards:
            card.update(board=board)

    def set_tintable(self):
        for card in self.cards:
            card.is_tintable = True

    def set_untintable(self):
        for card in self.cards:
            card.is_tintable = False

    def tint_all(self):
        for card in self.cards:
            card.tint()

    def untint_all(self):
        for card in self.cards:
            card.untint()


class PlayerGrid(BoxLayout):
    def __init__(self, **kwargs):
        super(PlayerGrid, self).__init__(**kwargs)


class Players(GridLayout):
    def __init__(self, **kwargs):
        super(Players, self).__init__(**kwargs)
        self.players = []
        self.action_labels = []

    def prepare_players(self, game, players):
        self.rows = len(players)

        for player_number, _ in enumerate(players):
            hand = game.hands[player_number + 1]
            self.players.append(
                (Hand(hand, False, False),
                 Hand(hand, True, True))
            )

        for i, (h1, h2) in enumerate(self.players, 2):
            box1 = PlayerGrid()
            box2 = PlayerGrid()
            box2.size_hint = 1, 1

            action_label = Label(text='n/a')
            self.action_labels.append(action_label)

            box2.add_widget(Label(text='Last action:'))
            box2.add_widget(action_label)

            box1.add_widget(Label(text='Player {0}'.format(i)))
            box1.add_widget(box2)

            self.add_widget(box1)
            self.add_widget(h1)
            self.add_widget(h2)

    def update_player(self, player_number, info_msg):
        self.action_labels[player_number].text = info_msg

    def set_tintable(self):
        for _, hand in self.players:
            hand.set_tintable()

    def set_untintable(self):
        for _, hand in self.players:
            hand.set_untintable()

    def tint_all(self):
        for _, hand in self.players:
            hand.tint_all()

    def untint_all(self):
        for _, hand in self.players:
            hand.untint_all()

    def update(self):
        for hand1, hand2 in self.players:
            hand1.update()
            hand2.update()


class Human(BoxLayout):
    def __init__(self, **kwargs):
        super(Human, self).__init__(**kwargs)

    def set_hand(self, game):
        self.hand = Hand(game.hands[0], full_info=False, is_tintable=True)
        self.hand.label.text = 'Your hand'
        self.add_widget(self.hand)
        self.tint_all()

    def set_tintable(self):
        self.hand.set_tintable()

    def set_untintable(self):
        self.hand.set_untintable()

    def tint_all(self):
        self.hand.tint_all()

    def untint_all(self):
        self.hand.untint_all()

    def update(self):
        self.hand.update()


class Board(BoxLayout):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)

    def set_cards(self, game):
        self.hand = Hand(
            self.board_state_to_cards(game.board_state),
            full_info=True,
            is_tintable=False
        )
        self.hand.label.text = 'Board state'
        self.add_widget(self.hand)

    def board_state_to_cards(self, board_state):
        cards = []
        hand_position = 0
        for key, value in board_state.items():
            if value == 0:
                rank = None
            else:
                rank = card.Rank(value)

            new_card = card.Card(rank, key)
            new_card.is_on_board = True
            new_card.hand_position = hand_position
            hand_position += 1
            cards.append(new_card)

        return cards

    def update(self):
        self.hand.update(board=True)


class EndGamePopup(Popup):
    score_label = ObjectProperty(None)
    quit_button = ObjectProperty(None)
    return_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EndGamePopup, self).__init__(**kwargs)
        Clock.schedule_once(self.bind_buttons, 0)

    def bind_buttons(self, *args):
        self.quit_button.bind(state=self.quit)
        self.return_button.bind(state=self.ret)

    def show(self):
        score = sum(hanabi_game.game.board_state.values())
        self.score_label.text = 'Final score: {0}'.format(score)
        self.open()

    def quit(self, instance, value):
        if value == 'normal':
            sys.exit(0)

    def ret(self, instance, value):
        if value == 'normal':
            self.dismiss()


class HanabiGame(BoxLayout):
    players = ObjectProperty(None)
    human = ObjectProperty(None)
    board = ObjectProperty(None)

    game_info = ObjectProperty(None)
    game_buttons = ObjectProperty(None)
    top_grid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(HanabiGame, self).__init__(**kwargs)
        self.player_choice = None
        self.play_discard = True
        self.hint = False
        self.end_game_popup = EndGamePopup()

    def prepare_game(self, other_players, hint):
        human_player = HumanPlayer()
        self.game = game.Game([human_player] + other_players, None, log=False)
        self.players.prepare_players(self.game, other_players)
        self.human.set_hand(self.game)
        self.board.set_cards(self.game)
        self.game_info.update(self.game)
        self.players.set_untintable()
        self.top_grid.size_hint = (1, hint)

    def play_discard_toggled(self):
        if self.hint and not self.game.is_game_over():
            self.human.set_tintable()
            self.human.tint_all()
            self.players.untint_all()
            self.players.set_untintable()
            self.hint = False
            self.play_discard = True
            self.player_choice = None

    def hint_toggled(self):
        if self.play_discard and not self.game.is_game_over():
            self.human.untint_all()
            self.human.set_untintable()
            if self.game.hints != 0:
                self.players.set_tintable()
                self.players.tint_all()
            self.hint = True
            self.play_discard = False
            self.player_choice = None

    def tint_all(self):
        self.players.tint_all()
        self.human.tint_all()

    def untint_all(self):
        self.players.untint_all()
        self.human.untint_all()

    def update(self):
        if self.game.is_game_over():
            self.end_game_popup.show()
            return

        if self.game.player_turn == 0:
            if self.player_choice is None:
                return

            self.player_choice.tint()

            if self.game_buttons.play_toggle.state == 'down':
                choice = Choice.PLAY
            elif self.game_buttons.discard_toggle.state == 'down':
                choice = Choice.DISCARD
            else:
                choice = Choice.HINT

            if choice is Choice.PLAY or choice is Choice.DISCARD:
                self.player_choice = utils.ChoiceDetails(
                    choice,
                    self.player_choice.hand_position
                )
            else:
                if self.game_buttons.hint_rank_toggle.state == 'down':
                    details = self.player_choice.real_rank
                else:
                    details = self.player_choice.real_suit

                self.player_choice = utils.ChoiceDetails(
                    Choice.HINT,
                    utils.HintDetails(
                        self.player_choice.player_number,
                        details
                    )
                )

            self.game.make_move()
            self.player_choice = None

        while self.game.is_game_over() is False:
            info_msg = self.game.make_move()
            self.players.update_player(
                self.game.prev_player_number() - 1,
                info_msg
            )

            if self.game.player_turn == 0:
                break

        if self.game.hints == 0:
            self.players.untint_all()
            self.players.set_untintable()
            self.player_choice = None

        self.game_info.update(self.game)
        self.players.update()
        self.human.update()
        self.board.update()

        if self.game.is_game_over():
            self.human.set_tintable()
            self.human.untint_all()
            self.human.set_untintable()
            self.players.set_tintable()
            self.players.untint_all()
            self.players.set_untintable()

            self.end_game_popup.show()


class HanabiApp(App):
    def __init__(self, players, hint, **kwargs):
        super(HanabiApp, self).__init__(**kwargs)
        self.players = players
        self.hint = hint

    def build(self):
        game = HanabiGame()
        game.prepare_game(self.players, self.hint)
        globals()['hanabi_game'] = game
        return game


if __name__ == '__main__':
    window_sizes = [
        (1600, 800, 0.9),
        (1600, 1130, 0.7),
        (1600, 1450, 0.4),
        (1600, 1600, 0.3)
    ]

    players = list(
        map(
            lambda x: globals()[x.get()](),
            filter(
                lambda x: x.get() != 'None',
                choice_boxes
            )
        )
    )

    x, y, hint = window_sizes[len(players) - 1]

    if platform == 'macosx':
        x /= 2
        y /= 2

    Window.size = x, y
    HanabiApp(players, hint).run()
