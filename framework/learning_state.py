# -*- coding: utf-8 -*-

import pickle


class LearningState:
    def __init__(self, reset=False):
        self.own_card_states = {}
        self.hint_states = {}
        self.macro_states = {}
        self.score_history = [3, 3]
        self.states_history = []
        self.max_state_history = 400
        if reset is False:
            self.load_knowledge()

    def load_knowledge(self):
        with open('own_card_states.data', 'rb') as file:
            self.own_card_states = pickle.load(file)
        with open('hint_states.data', 'rb') as file:
            self.hint_states = pickle.load(file)
        with open('macro_states.data', 'rb') as file:
            self.macro_states = pickle.load(file)
        with open('score_history.data', 'rb') as file:
            self.score_history = pickle.load(file)

    def save_knowledge(self):
        with open('own_card_states.data', 'wb') as file:
            pickle.dump(self.own_card_states, file, protocol=pickle.HIGHEST_PROTOCOL)
        with open('hint_states.data', 'wb') as file:
            pickle.dump(self.hint_states, file, protocol=pickle.HIGHEST_PROTOCOL)
        with open('macro_states.data', 'wb') as file:
            pickle.dump(self.macro_states, file, protocol=pickle.HIGHEST_PROTOCOL)
        with open('score_history.data', 'wb') as file:
            pickle.dump(self.score_history, file, protocol=pickle.HIGHEST_PROTOCOL)

    def get_own_card_weights(self, state):
        if state not in self.own_card_states:
            self.own_card_states[state] = [[3, 1, (1, 0), (1, 1), (1, 0)], [3, 1, (1, 0), (1, 1), (1, 0)]]
        return self.own_card_states[state]

    def get_hint_weights(self, state):
        if state not in self.hint_states:
            self.hint_states[state] = [[2, 1, (1, 0), (1, 1)]]
        return self.hint_states[state]

    def get_macro_weights(self, state):
        if state not in self.macro_states:
            self.macro_states[state] = [[3, 1, (1, 0), (1, 1), (1, 0)], [3, 1, (1, 0), (1, 1), (1, 0)],
                                        [3, 1, (1, 0), (1, 1), (1, 0)]]
        return self.macro_states[state]

    def get_chance(self, weights):
        size = len(weights)-2

        sum_n = 0
        sum_m = 0
        for i in range(-1, -size-1, -1):
            sum_n += (weights[i][0]*(size+i+1))/size
            sum_m += (weights[i][1]*(size+i+1))/size

        return sum_m/sum_n

    def append_to_history(self, round_states):
        self.states_history.append(round_states)

    def get_last_hint_state(self):
        return [self.states_history[-1][2][0], self.states_history[-1][5][0]]
