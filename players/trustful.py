# -*- coding: utf-8 -*-

from .base_trustful import *

debug = False


class Trustful(BasePlayer, BaseTrustful):
    def __init__(self, *args):
        super(Trustful, self).__init__(*args)
        self.name = 'Trustful'
        self.card_hint_type = {}
        self.hand_size = 5

    def check_for_good_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        play_tip = self.check_for_play_tip(
            round_info, player_number, only_next_player=only_next_player)
        if play_tip is not False:
            return play_tip

        if debug and round_info.log:
            self.info("Discard:")
        discard_tip = self.check_for_discard_tip(
            round_info, player_number, only_next_player=only_next_player)
        return discard_tip

    def check_for_risky_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        return self.check_for_play_tip(round_info, player_number, 0.9, 0.3, -1.6, only_next_player=only_next_player)

    def check_for_information_tip(self, round_info, player_number, only_next_player=False):
        if round_info.hints <= 1:
            return False

        return self.check_for_play_tip(round_info, player_number, hint_pass_score=0.65, information_tip_value=0.7,
                                       already_has_play_multiplier=1.0, only_next_player=only_next_player)

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
