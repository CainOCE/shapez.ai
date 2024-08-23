### file containing network framework

import tensorflow as tf
import keras
import numpy as np
import matplotlib.pyplot as plt
import copy

optimiser = keras.optimizers.Adam(learning_rate=0.001)

# list of possible inputs
# smaller the better, as stated above
#    reduce amount buildings which can be placed
input_space = ["B", "E"] # for now only allowing - belt (B) and extractor (E)

# list of possible actions
# technically the action space is a function of:
#   the amount of empty blocks in the desginated space (E)
#   the amount of possible inputs + rotations (I)
#   therefore, size(A) = I * E -- which could grow very quickly. model go slow

# to minimise this size we can:
#   1. reduce possible inputs
#       - only allow a selection of buildings, most simple at first only allow belts
#   2. reduce positions we allow the model to place stuff
#       - only allow model to place stuff next to pre-existing structures
# would shape of this be a 2d array or maybe dictionary:
#   possible squares as keys? adding an element would normally increase
#   action space by 3, remove 1 cell which has been added to
action_space = []

# some heuristic function to determine how "good" a state is
# this approach is more in line with a traditional q-learning model
# where we as humans define the heuristic.
# ideally we want to model to do this itself
def heuristic(state, goal):
    # state is some array of the board
    #   may be a condensed/zoomed in version of the board
    #   only focus on part of the board that matters right now
    # goal is the current goal (eg. 30x squares)
    return 0

# like described above, get free spaces which are next to a resource/building
def get_available_spaces(state):
    # assume state is 2d array
    # assume "empty" cell is signified by 0
    spaces = set()
    occupied = []
    cols = len(state)
    rows = len(state[0])
    # add all full cells to a list first
    for i in range(cols):
        for j in range(rows):
            if state[i][j] != 0:
                occupied.append((i, j))
    # add unoccupied neighbor cells to spaces
    for i in range(cols):
        for j in range(rows):
            if state[i][j] != 0:
                # add adjacent cells, used set no dont have to worry about duplicates
                if (i+1, j) not in occupied:
                    spaces.add((i+1, j))
                if (i-1, j) not in occupied:
                    spaces.add((i-1, j))
                if (i, j+1) not in occupied:
                    spaces.add((i, j+1))
                if (i, j-1) not in occupied:
                    spaces.add((i, j-1))
    # convert spaces to list and return
    return list(spaces)

# very crude way of getting state after some in action in some pos
def get_next_state(state, pos, action):
    i = pos[0]
    j = pos[1]
    new_state = copy.deepcopy(state)
    new_state[i][j] = action
    return new_state

# is this useful????
def create_action_space(input_space, empty_neighbours):
    actions, spaces = np.meshgrid(input_space, empty_neighbours)
    return actions, spaces

# test for get spaces
X = np.zeros((5,5))
X[1][1] = 2
empty_neighbours = get_available_spaces(X)
actions, spaces = create_action_space(input_space, empty_neighbours)

# classic Q-learning model -- no machine learning
class qLearn:
    def __init__(self, initial_state, inputs):
        self.state = initial_state
        self.inputs = inputs

    def update_state(self, new_state):
        self.state = new_state

    def next_best_move(self):
        available_spaces = get_available_spaces(self.state)
        current_best_score = -10000 # current best move
        best_move = None
        best_move_pos = None
        for space in available_spaces:
            for action in self.inputs:
                next_state = get_next_state(self.state, space, action)
                score = heuristic(next_state)
                if score > current_best_score:
                    current_best_score = score
                    best_move = action
                    best_move_pos = space
        return best_move_pos, best_move

# Neural Network class
class Network:
    def __init__(self):
        pass

    def train():
        """
        unsupervised training
            - would require very good goal/loss function

        supervised training:
            - would require training data, how can we get that?
        """
        pass




