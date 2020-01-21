# -*- coding: utf-8 -*-


class BayesianParameters:
    def __init__(self, discard_tip, good_tip, risky_tip, information_tip):
        self.discard_tip_parameters = discard_tip
        self.good_tip_parameters = good_tip
        self.risky_tip_parameters = risky_tip
        self.information_tip_parameters = information_tip
