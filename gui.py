import sys
import os
#os.environ['KIVY_NO_CONSOLELOG'] = '1'

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
from kivy.utils import platform


class HumanPlayer(base_player.BasePlayer):
    def __init__(self, game, *args):
        super(HumanPlayer, self).__init__(*args)
        self.name = 'Player'

    def play(self, round_info):
        return game.player_choice
        """
        possible_plays = round_info.true_hand_info().playable_cards(round_info)

        if len(possible_plays) == 0:
            return ChoiceDetails(
                Choice.DISCARD,
                choice(round_info.player_hand).hand_position
            )

        else:
            return ChoiceDetails(
                Choice.PLAY,
                choice(possible_plays).hand_position
            )


        # hint example:
        from framework import HintDetails, Suit
        return ChoiceDetails(Choice.HINT, HintDetails(abs(round_info.player_turn - 1), Suit.GREEN))
        """


class GameInfo(BoxLayout):
    def __init__(self, **kwargs):
        super(GameInfo, self).__init__(**kwargs)

    def update(self, game):
        pass


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

    def next_turn(self, instance, value):
        print('next turn')


class Card(Image):
    def __init__(self, card, full_info, **kwargs):
        super(Card, self).__init__(**kwargs)
        self.size_hint = 1, 1

        self.full_info = full_info
        self.is_tinted = False

        self.set_card(card)
        self.update()

    def set_card(self, card):
        self.card = card
        self.hand_position = card.hand_position
        self.real_rank = card.real_rank
        self.real_suit = card.real_suit
        self.revealed_rank = card.revealed_rank
        self.revealed_suit = card.revealed_suit

    def enable_tint(self):
        self.is_tinted = True
        self.color = (0.5, 0.5, 0.5, 0.8)

    def disable_tint(self):
        self.is_tinted = False
        self.color = (1, 1, 1, 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.is_tinted:
                self.disable_tint()
            else:
                self.enable_tint()

    def update(self):
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


class Hand(BoxLayout):
    def __init__(self, hand, full_info, **kwargs):
        super(Hand, self).__init__(**kwargs)
        self.box = BoxLayout(orientation='horizontal')
        self.box.spacing = 5
        self.full_info = full_info
        self.cards = []

        for new_card in hand:
            self.cards.append(Card(new_card, full_info))

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


class PlayerGrid(BoxLayout):
    def __init__(self, **kwargs):
        super(PlayerGrid, self).__init__(**kwargs)


class Players(GridLayout):
    def __init__(self, **kwargs):
        super(Players, self).__init__(**kwargs)
        self.players = []

    def prepare_players(self, game, players):
        self.rows = len(players)

        for player_number, _ in enumerate(players):
            hand = game.hands[player_number + 1]
            self.players.append((Hand(hand, False), Hand(hand, True)))

        for i, (h1, h2) in enumerate(self.players, 2):
            box1 = PlayerGrid()
            box2 = PlayerGrid()
            box2.size_hint = 1, 1

            self.action_label = Label(text='n/a')

            box2.add_widget(Label(text='Last action:'))
            box2.add_widget(self.action_label)

            box1.add_widget(Label(text='Player {0}'.format(i)))
            box1.add_widget(box2)

            self.add_widget(box1)
            self.add_widget(h1)
            self.add_widget(h2)

    def update(self, game):
        for obj in self.walk(restrict=True):
            if hasattr(obj, 'is_player'):
                print(obj)


class Human(BoxLayout):
    def __init__(self, **kwargs):
        super(Human, self).__init__(**kwargs)

    def set_hand(self, game):
        self.hand = Hand(game.hands[0], full_info=False)
        self.hand.label.text = 'Your hand'
        self.add_widget(self.hand)

    def update(self):
        for c in self.hand:
            c.update()


class Board(BoxLayout):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)

    def set_cards(self, game):
        self.hand = Hand(
            self.board_state_to_cards(game.board_state),
            full_info=True
        )
        self.hand.label.text = 'Board state'
        self.add_widget(self.hand)

    def board_state_to_cards(self, board_state):
        cards = []
        for key, value in board_state.items():
            if value == 0:
                rank = None
            else:
                rank = card.Rank(value)

            new_card = card.Card(rank, key)
            new_card.is_on_board = True
            cards.append(new_card)

        return cards

    def update(self):
        for c in self.hand:
            c.update()


class HanabiGame(BoxLayout):
    players = ObjectProperty(None)
    human = ObjectProperty(None)
    board = ObjectProperty(None)

    game_info = ObjectProperty(None)
    top_grid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(HanabiGame, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.game = None
        self.player_choice = None

    def prepare_game(self, other_players, hint):
        human_player = HumanPlayer(self)
        self.game = game.Game([human_player] + other_players, None, log=False)
        self.players.prepare_players(self.game, other_players)
        self.human.set_hand(self.game)
        self.board.set_cards(self.game)
        self.top_grid.size_hint = (1, hint)

    def play(self):
        pass

    def discard(self):
        pass

    def hint(self):
        pass

    def update(self, event):
        pass


class HanabiApp(App):
    def __init__(self, players, hint, **kwargs):
        super(HanabiApp, self).__init__(**kwargs)
        self.players = players
        self.hint = hint

    def build(self):
        game = HanabiGame()
        game.prepare_game(self.players, self.hint)
        # from kivy.clock import Clock
        # Clock.schedule_interval(game.print_size, 1.0 / 60.0)
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
