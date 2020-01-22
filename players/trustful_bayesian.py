# -*- coding: utf-8 -*-

from .trustful_base import *

debug = False


class TrustfulBayesian(BasePlayer, TrustfulBase):
    def __init__(self, *args):
        super(TrustfulBayesian, self).__init__(*args)
        self.name = 'Bayesian Trustful'
        self.card_hint_type = {}
        self.discard_tip = [3.9675791022130866, -1.2236154016668084, 1.1064941122662877]
        self.good_tip = [0.6965048774115057, 0.4938063699231073, -5.096989475985786, 1.179651463460699,
                         1.1499780740878032, 0.1048895757841592, 0.0601224261044882, 1.7313274701206363]
        self.risky_tip = [3.980842278702617, 0.6920787372911628, -6.639852782714435, 0.9957316072619526,
                          1.0015038969624326, -0.21132160122235594, -0.03166823189565862, 1.7027964810065506]
        self.information_tip = [2.383727091348472, 0.29295269431507714, -8.866676889247437, 1.0304108640224716,
                                1.1222361825640925, 0.48807000478174384, 0.30540840945292064, 1.4982700221551264]
        self.hand_size = 5

    def check_for_good_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        play_tip = self.check_for_play_tip(round_info, player_number, self.good_tip[0], self.good_tip[1],
                                           self.good_tip[2], self.good_tip[3], self.good_tip[4], self.good_tip[5],
                                           self.good_tip[6], self.good_tip[7], only_next_player=only_next_player)
        if play_tip is not False:
            return play_tip

        if debug and round_info.log:
            self.info("Discard:")
        discard_tip = self.check_for_discard_tip(round_info, player_number, self.discard_tip[0], self.discard_tip[1],
                                                 self.discard_tip[2], only_next_player=only_next_player)
        return discard_tip

    def check_for_risky_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        return self.check_for_play_tip(round_info, player_number, self.risky_tip[0], self.risky_tip[1],
                                       self.risky_tip[2], self.risky_tip[3], self.risky_tip[4], self.risky_tip[5],
                                       self.risky_tip[6], self.risky_tip[7], only_next_player=only_next_player)

    def check_for_information_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        return self.check_for_play_tip(round_info, player_number, self.information_tip[0], self.information_tip[1],
                                       self.information_tip[2], self.information_tip[3], self.information_tip[4],
                                       self.information_tip[5], self.information_tip[6], self.information_tip[7],
                                       only_next_player=only_next_player)

    def play(self, round_info):
        if round_info.current_turn == 0:
            self.initialize_card_hint_history(round_info)

        if debug and round_info.log:
            self.info("{0}".format(self.card_hint_type))

        self.check_play_history(round_info)

        if debug and round_info.log:
            self.info("{0}".format(self.card_hint_type))

        if round_info.hints is utils.MAX_HINTS:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_good_tip, self.check_for_risky_tip, self.check_for_save_tip,
                            self.check_for_information_tip, self.check_for_obvious_discard, self.check_for_guess_discard]
        elif round_info.hints >= 6:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_good_tip, self.check_for_obvious_discard, self.check_for_risky_tip,
                            self.check_for_save_tip, self.check_for_guess_discard]
        elif round_info.hints >= 3:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_good_tip, self.check_for_obvious_discard, self.check_for_guess_discard]
        else:
            action_order = [self.check_for_necessary_tip, self.check_for_obvious_play, self.check_for_hinted_play,
                            self.check_for_obvious_discard, self.check_for_good_tip, self.check_for_guess_discard]

        for action in action_order:
            if debug and round_info.log:
                self.info('{0}'.format(action))
            decision = functools.partial(action, round_info, round_info.player_turn)()
            if decision is not False:
                return decision
