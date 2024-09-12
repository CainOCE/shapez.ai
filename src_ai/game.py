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

class shapezGym(gym.Env):

    # buildings is some dictionary like
    # {0: "empty", 1: "HUB", 2: "EXTRACTOR", ...}
    # account for resources
    # -1 --> triangle
    # -2 --> square

    # need some way of passing goal information into program at each state
    # could pre program in goals if they are always the same
    # goals = [(("triangles", 10)), ... (("half-circle-half-sqaure", 10))]
    # unless find this information in the soruce code, probably more realistic

    # TODO:
    # 1. encode products (likely some like hex/hash number describing all possible products)
    #       - 1crcrcrcr -- red circle, idk just example
    # 2. write code to check if something was produced since last action -- kind of links with idea below
    # 3. find a way to account for which state gets reward added, given products take
    #    some time to arrive at HUB --- may cause slight misoptimisation
    #       - even better if we could have a list of products currently on belt
    #       - then another check to see what hits HUB

    def __init__(self, buildings, size, state, goals):

        self.buildings = buildings # dictionary of buildings and a given index
        self.size = size # side length of the "board", centre around the HUB
        self.goals = goals # dictionary containing the goals of the game (or some small subset of goals)
        self.num_actions = len(buildings.keys()) # number of possible values of each cell
        self.state = state
        # example from chess
        #self.observation_space = spaces.Box(-16, 16, (8, 8))  # board 8x8
        #self.action_space = spaces.Discrete(64 * 16 + 4)



        self.observation_space = spaces.Box(0, self.num_actions, (size, size))
        self.action_space = spaces.Discrete(size**2 * self.num_actions)



    """
    # naive approach
    # any building on any possible grid -- (size^2 * num_actions)
    ###
    # my idea: lmk if you can think of better
    # if resource --> extractor
    # if empty --> belt
    # if belt --> delete
    # if building --> delete
    """
    def get_possible_moves(self, state):
        # to be implemented
        actions = set()

        for i in state:
            for j in state[0]:
                cell_val = state[i][j]
                if cell_val == 'empty':
                    actions.add((i, j, 'belt'))
                if cell_val == 'resource':
                    actions.add((i,j,'extractor'))

        return actions


    def check_produced(self):
        # check if anything has reached the HUB
        # alternatviely, check what is currently on belts
        pass

    def update_goal(self, product):

        # minus from product goal
        self.goals.update({product: self.goals.get(product) - 1})

        # if zero more required, remove
        if self.goals.get(product) == 0:
            self.goals.pop(product)







    # update the goals because all previous goals have been met
    # maybe even smarter to do this in 2 or 3 level batches???
    def update_goals(self, new_goals):

        for goal in new_goals: # list of goals to be added
            self.goals.update(goal)


    def step(self, state, action):
        # action should already be legal

        i, j, m = action
        state[i][j] = m
        reward = 0

        produced = self.check_produced()
        if produced in self.goals.keys():
            ## this wont reward properly as it will reward some state some number of actions
            ## after the last building placed was involved
            ## in bad cases this will negatively reward model
            ## eg. 1. product travelling to HUB
            #      2. belt behind product is deleted
            #      3. no more product can come through
            #      4. but first state after product gets to HUB gets reward

            # could reduce probability of deleting belt,
            # or increase probability of doing action in a free space?

            ######
            # not sure how to officially solve this without manually checking a
            # path still exists. seems slow
            #
            # the case described above will be rareish, at least for small factory
            # relative to size
            ####

            # if thing has reach the HUB --> update_goal
            self.update_goal(produced)

            reward += 1 # just add one if something produced is in goals

        return state, reward





