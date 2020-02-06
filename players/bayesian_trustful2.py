# -*- coding: utf-8 -*-

from .base_trustful import *

debug = False


class BayesianTrustful2(BasePlayer, BaseTrustful):
    def __init__(self, *args):
        super(BayesianTrustful2, self).__init__(*args)
        self.name = 'BayesianTrustful2'
        self.card_hint_type = {}
        self.discard_tip = [3.1157470722431895, -5.870410617419754, 1.0362370768397047]
        self.good_tip = [0.7266001731976601, 0.8445165587967782, -6.8459259143424065, 1.2702664568412567,
                         1.2260569959609633, -0.029150069963995606, 0.030675336013306742, 1.706607934110137]
        self.risky_tip = [0.5780771996803791, 0.3539543081924703, -1.9985924494738576, 0.8527851486282219,
                          0.9361585298158691, 0.37366070452122724, 0.199403268481135, 1.6905365910487746]
        self.information_tip = [4.190677973445652, 0.41939489562396703, -9.258053259676274, 0.7326838798720842,
                                1.1746671578885395, 0.2818988936771667, -0.15801457452508066, 1.3402675677953646]
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
            decision = functools.partial(
                action, round_info, round_info.player_turn)()
            if decision is not False:
                return decision
