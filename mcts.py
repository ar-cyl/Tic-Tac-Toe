import math
import numpy as np
from sanic.response import json
from board import *
import random
from copy import deepcopy

ROOT = [[0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]]

# #TODO: bit representation for state 
# class State:
#     def __init__(self, player_states, whose_turn=1):
#         self.whose_turn=whose_turn-1
#         self.player_states = player_states
#         self.legal_actions = self.get_legal_actions()

#     def __str__(self):
#         return [bin(self.player_states[0]), bin(self.player_states[1])]

#     def to_bit(self, action):
#         return 1 << (action[0]*3 +action[1])

#     #expects action as a tuple of valid location of next action, e.g. (2,1)
#     def move(self, action):
#         if self.is_valid_action(action):
#             next_states = deepcopy(self.player_states)
#             self.player_states[self.whose_turn%2] |= self.to_bit(action)
#         return State(player_states = next_states, whose_turn=self.whose_turn+1)
        

#     def is_winning(self, bitValue):
#         return (
#             ((bitValue & 0b000000111) == 0b000000111) or
#             ((bitValue & 0b000111000) == 0b000111000) or 
#             ((bitValue & 0b111000000) == 0b111000000) or
#             ((bitValue & 0b100100100) == 0b100100100) or
#             ((bitValue & 0b010010010) == 0b010010010) or
#             ((bitValue & 0b001001001) == 0b001001001) or 
#             ((bitValue & 0b100010001) == 0b100010001) or
#             ((bitValue & 0b001010100) == 0b001010100)
#         )

#     def is_terminal_state(self):
#         is_end = False

#         if self.is_winning(self.player_states[0]):
#             winner = 0
#             is_end = True
#         elif self.is_winning(self.player_states[1]):
#             winner = 1
#             is_end = True
        
#         elif len(self.get_legal_actions()) == 0:
#             # print("hereee")
#             return True, 0.5
#         else:
#             return False, 0
        
#         if winner == self.whose_turn%2:
#             score = 0
#         else:
#             score = 1
#         return is_end, score
        
    

#     def is_valid_action(self, action):
#         position = self.to_bit(action)
#         return self.player_states[self.whose_turn%2] & position == position


#     def get_legal_actions(self):
#         #hardcoded
#         legal_actions = []
#         for row in range(3):
#             for column in range(3):
#                 if self.is_valid_action((row, column)):
#                     legal_actions.append((row, column))
#         return legal_actions


class State:
    def __init__(self, raw_state, whose_turn=1):
        self.raw_state = raw_state
        self.whose_turn = whose_turn
        self.legal_actions = self.get_legal_actions()

    def to_bit(self, action):
        return 1 << (action[0]*3 +action[1])

    #expects action as a tuple of valid location of next action, e.g. (2,1)
    def move(self, action):
        if self.is_valid_action(action):
            next_state = deepcopy(self.raw_state)
            next_state[action[0]][action[1]] = self.whose_turn
            next_whose_turn = 2 if self.whose_turn == 1 else 1
        return State(raw_state=next_state, whose_turn=next_whose_turn)
        

    def separate_states(self):
        state = deepcopy(self.raw_state)
        player1_state = ""
        player2_state = ""
        for row in range(3):
            for col in range(3):
                if state[row][col] == 1:
                    player1_state+="1"
                    player2_state+="0"
                elif state[row][col] == 2:
                    player2_state+="1"
                    player1_state+="0"
                else:
                    player1_state += "0"
                    player2_state += "0"
        return int(player1_state, 2), int(player2_state, 2)

    def is_winning(self, bitValue):
        return (
            ((bitValue & 0b000000111) == 0b000000111) or
            ((bitValue & 0b000111000) == 0b000111000) or 
            ((bitValue & 0b111000000) == 0b111000000) or
            ((bitValue & 0b100100100) == 0b100100100) or
            ((bitValue & 0b010010010) == 0b010010010) or
            ((bitValue & 0b001001001) == 0b001001001) or 
            ((bitValue & 0b100010001) == 0b100010001) or
            ((bitValue & 0b001010100) == 0b001010100)
        )

    def is_terminal_state(self):
        is_end = False
        player1_state, player2_state = self.separate_states()
        if self.is_winning(player1_state):
            winner = 1
            is_end = True
        elif self.is_winning(player2_state):
            winner = 2
            is_end = True
        
        elif len(self.legal_actions) == 0:
            return True, 0.5
        else:
            return False, 0
        
        if winner == self.whose_turn:
            score = 0
        else:
            score = 1
        return is_end, score
        
    def is_valid_action(self, action):
        return self.raw_state[action[0]][action[1]] == 0

    def get_legal_actions(self):
        legal_actions = []
        for row in range(3):
            for column in range(3):
                if self.is_valid_action((row, column)):
                    legal_actions.append((row, column))
        return legal_actions


class Node:
    def __init__(self, state, action=None, parent=None):
        self.w = 0
        self.n = 0
        self.state = state
        self.action = action
        self.parent = parent
        self.children = []
        self.untried_actions = self.state.get_legal_actions()

    def is_terminal_node(self):
        return self.state.is_terminal_state()

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.move(action)
        child_node = Node(
            next_state, action=action, parent=self
        )
        self.children.append(child_node)
        return child_node

    def best_child(self, T, c_param=1.41):
        choices_weights = [
            (c.w / c.n) + c_param * np.sqrt((np.log(T) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]
    
    def most_visited_child(self):
        return self.children[np.argmax([c.n for c in self.children])].action

    
#rollout random policy and get result
def random_policy(state:State):
    while not state.is_terminal_state()[0]:
        action = random.choice(state.legal_actions)
        state = state.move(action)
    return state.is_terminal_state()[1]


class MCTS:
    def __init__(self, root_state):
        self.root = Node(root_state)
        self.current_node = self.root
        self.T = 0

    #rollout random policy and get final result
    def rollout(self):
        result = random_policy(deepcopy(self.current_node.state))
        self.T += 1
        return result
    
    #backpropagate win score upward upto root and update simulation count
    def backpropagate(self, result):
        while self.current_node.parent != None:
            self.current_node.w += result
            self.current_node.n += 1
            self.current_node = self.current_node.parent
            result = 1-result
    
    #determine node to simulate
    def treepolicy(self):
        current_node = self.root
        while not current_node.is_terminal_node()[0]:
            if not current_node.is_fully_expanded():
                self.current_node = current_node.expand() 
                return
            else:
                current_node = current_node.best_child(T=self.T)
        self.current_node = current_node

    def return_action(self):
        return self.root.most_visited_child()
