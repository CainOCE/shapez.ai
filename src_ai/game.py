import gymnasium as gym
from gym import spaces
import numpy as np
import copy
from signals import ListenServer


#if we could make a simple python copy of the game could be useful... idk discuss w others

#during training will we require the chrome to be running, will make training super slow
#this is a where our version of the game could run much faster

#simplify as much as possible:
# Entities
# 0 - empty/delete
# 1 - HUB
# 2 - extractor
# 3 - belt_up
# 4 - belt_down
# 5 - belt_left
# 6 - belt_right
# ... more belts (12 total types)
# X - splitter
#
# Resources (different list) -- layering???
# crcrcrcr - circle
# etc.

# QUESTIONS
# is it possible to delete a resource?
#

 # pre made list since goals always remain the same
 # this way we can also make more very simple goals for basic training
goals = [{'crcrcrcr':10, 'abx':5}, # 1
         {'srsrsrsr': 20}, # 2
         ]

# NEEDS:
#   - way to restart game with new seed (tbd in reset())
#   - way to make action happen (step()) -- return new game state given a state and action
#   - way to check if anything has been produced (in check_produced())


 # communicator??
class shapezGym():

    def __init__(self, buildings, level=0):

        # make action map
        self.action_map = {
            'empty': 0,
            'extractor': 1
        }
        self.num_actions = len(self.action_map) # number of possible values of each cell

        self.goals = {} # array of goals

        self.level = level # start at level given, if not level 1
        # initial game for first time
        self.resource_map = {} # make map of resources
        self.state = None
        self.seed = 0
        _, _, _ = self.reset()

        self.size = self.state[0] # size of array -- make sure the game is square

        self.layer2 = np.zeros_like(self.state) # upper layer so buildings will go on here

        self.shapes_produced = {} # will contain all shapes produced, only increase

        self.communicator = ListenServer()

    def reset(self):
        '''
        reset game to new start with different seed
        update goals to initial goals
        return:
            - seed
            - starting state
        '''
        seed = 0 # need to call from game

        #idk something like
        # self.communicator.receive()

        string_state = [['belt', 'empty'], ['crcrcr', 'empty']] # example
        # need to call from game
        # state like (square is preferable)
        #  '  empty ', '  empty ', ...
        #  'crcrcrcr', ...
        #  'crcrcrcr',
        #     ...
        # like how ryan had found them
        self.resource_map = {x: hash(x) for x in self.get_resources(string_state)}
        print(self.resource_map)
        self.state = self.encode_state(string_state)
        # make numerical state from string_state
        # was thinking we make the value of a state a running count, so then layers could
        # somewhat be considered



        self.goals.clear() # remove all old goals
        self.goals.update(goals[self.level]) # add initial level

        return self.seed, self.state, self.resources

    def encode_state(self, string_state):
        state = np.zeros_like(string_state, dtype=float)
        for i in range(len(string_state)):
            for j in range(len(string_state[0])):
                value = string_state[i][j]
                # if in actions
                state[i][j] = self.action_map[value]
                # else get from resources
                state[i][j] = self.resource_map[value]
        return state

    # forgot why i thought this method would be useful but ive made it now
    # no useful for separating actions from resources in the available actions
    #
    def get_resources(self, state):
        resources = []
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] not in self.action_map.keys():
                    resources.append((i, j, state[i][j]))
        return resources

    # so only give minimum options for each square for simplicity
    # so:
    # empty square - place belt*12/building --- problem with defining belts
    # resource - place extractor
    # belt or building - delete
    #
    # need to thikn more about how to think about belts?
    # i think will promote placing down lots of belts tho which will be beneficial
    def get_possible_moves(self, state):
        # to be implemented
        actions = set()

        ### needs to be implemented
        for i in state:
            for j in state[0]:
                cell_val = state[i][j] # get value of cell (i, j)
                # map to action
                if self.action_map[cell_val] == 'empty':
                    actions.add((i, j, 1)) # add belt
                if cell_val == 'resource':
                    actions.add((i,j, 2))

        return actions

    def check_produced(self):

        product = None
        return product

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


test = shapezGym()



