# -*- coding: utf-8 -*-

import pickle


class LearningState:
    def __init__(self):
        self.own_card_states = {}
        self.hint_states = {}
        self.macro_states = {}
        self.score_history = [2, 2]
        #self.load_knowledge()
        self.states_history = []
        self.max_macro_size = 200

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
            self.own_card_states[state] = [[3, 1], [3, 1]]
        return self.own_card_states[state]

    def get_hint_weights(self, state):
        if state not in self.hint_states:
            self.hint_states[state] = [[2, 1]]
        return self.hint_states[state]

    def get_macro_weights(self, state):
        if state not in self.macro_states:
            self.macro_states[state] = [[1, 0, 1, 0], [1, 0, 1, 0], [1, 0, 1, 0]]
        return self.macro_states[state]

    def get_chance(self, weights):
        return weights[1] / weights[0]

    def get_macro_chance(self, weights):
        return weights[0] / (len(weights) - 1)

    def append_to_history(self, round_states):
        self.states_history.append(round_states)

    def get_last_hint_state(self):
        return self.states_history[-1][2][0], self.states_history[-1][5][0]
