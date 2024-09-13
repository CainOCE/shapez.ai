import gymnasium as gym
from gym import spaces
import numpy as np
import copy

"""
set up game in simple version like gym
- need a step function
-
"""

"""
if we could make a simple python copy of the game could be useful... idk discuss w others

during training will we require the chrome to be running, will make training super slow
this is a where our version of the game could run much faster

save model at end??

simplify as much as possible:
- extractors (1)
- belts (2)
- resource (-1, -2, -3, -4) -- or maybe some hash code like describing the products
- HUB (3)
- empty (0)

"""

goals = [] # pre made list since goals always remain the same


class shapezGym():

    def __init__(self, buildings):

        self.buildings = buildings # dictionary of buildings and a given index
        self.num_actions = len(buildings.keys()) # number of possible values of each cell
        self.action_map = {0:'empty', 1: 'belt'}

        self.goals = {} # array of goals
        self.level = 0 # start at level one
        self.state = self.reset() # get game state
        self.size = self.state[0] # size of array -- make sure the game is square



        self.shapes_produced = {}

        self.observation_space = spaces.Box(0, self.num_actions, (self.size, self.size))
        self.action_space = spaces.Discrete(self.size**2 * self.num_actions)


    def get_possible_moves(self, state):
        # to be implemented
        actions = set()

        ### needs to be implemented
        for i in state:
            for j in state[0]:
                cell_val = state[i][j] # get value of cell (i, j)

                if self.action_map[cell_val] == 'empty':
                    actions.add((i, j, 1)) # add belt
                if cell_val == 'resource':
                    actions.add((i,j, 2))

        return actions

    """

    """
    def check_produced(self):

        product = None
        return product

    """

    """
    def update_goal(self, product):

        # minus from product goal if desired product
        if product in self.goals.keys():
            self.goals.update({product: self.goals.get(product) - 1})

            # if zero more required, remove
            if self.goals.get(product) == 0:
                self.goals.pop(product)
                return True # goal is completed
            return False
        return False

    # update the goals because all previous goals have been met
    # maybe even smarter to do this in 2 or 3 level batches???
    def update_goals(self):

        self.goals.clear()
        self.level += 1
        for goal in goals[self.level]:
            self.goals.update({goal}) # may need to tweak how goals is setup




    def reset(self):
        '''
        reset game to new start with different seed
        update goals to initial goals
        return:
            - seed
            - starting state
        '''
        self.goals.clear() # remove all old goals
        return 0, np.array((2, 2))


    def step(self, action):
        '''
        make one "step" through the game environment given an action

        return:
            - new state
            - reward (reward for being in this state)
            - reached
        '''

        i, j, m = action
        self.state[i][j] = m # update state
        reward = 0
        reached = False

        produced = self.check_produced()
        if produced in self.goals.keys():

            reached = self.update_goal(produced)

            # cehck if goal was completed this step
            if reached and len(self.goals) == 0:
                reward += 5 # big reward for completing a level
                self.update_goals()
            reward += 1 # just add one if something produced is in goals

        return self.state, reward





