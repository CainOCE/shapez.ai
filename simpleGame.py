## simplified version of the game
# Rhys Tyne

import numpy as np
import random
import llist

class Game:
    def __init__(self, size, inputs):
        if size % 2 == 0: # make grid have an exact centre
            size +=1
        self.size = size
        self.board = np.zeros((self.size, self.size))
        # made up custom goals
        self.goals = [[(-2, 30)],
                      [(-3, 10), (-4, 25)]
        ]
        self.generate_board()
        self.inputs = inputs
        # (may need to specify different types of belt)


    # create some structures
    def generate_board(self):
        # builtin blocks
        # 0 -- empty cell
        # -1 -- Acceptor
        # -2 -- resource A
        # -3 -- resource B

        # make user placeable objects have positive action number for easy check
        # 1 -- extractor
        # 2 -- belt
        # 3 --

        # make central acceptors
        centre_index = int((self.size-1)/2)
        for i in range(-1,2):
            for j in range(-1,2):
                self.board[int((self.size-1)/2) + i][int((self.size-1)/2) + j] = -1

        # make some resources
        possible_spots = [[np.floor(centre_index/2), np.floor(centre_index/2)],
                              [np.floor(centre_index/2), centre_index+np.ceil(centre_index/2)],
                              [centre_index+np.ceil(centre_index/2), np.floor(centre_index/2)],
                              [centre_index+np.ceil(centre_index/2), centre_index+np.ceil(centre_index/2)]
                              ]
        random.shuffle(possible_spots)
        for p in range(3): # number of resource "piles"
            pos = possible_spots[p]
            val = -p-2
            resource_centre = (int(pos[0]), int(pos[1]))
            for i in range(-1,2):
                for j in range(-1,2):
                    self.board[resource_centre[0] + i][resource_centre[1] + j] = val





class Extractor:
    # goes on a resource, ie. cell value <= -2
    def __init__(self, out_direction):
        self.out_direction = out_direction
        self.value = 1


class Belt:
    def __init__(self, in_direction, out_direction):
        self.value = 2
        self.in_direction = in_direction
        self.out_direction = out_direction


class BeltLine:
    def __init__(self):
        self.belts = llist.sllist()
