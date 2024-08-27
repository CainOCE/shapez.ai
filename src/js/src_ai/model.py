# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:41

@author: Cain Bruhn-Tanzer
"""


class Model:
    """ An abstract model class for AI development. """

    def __init__(self):
        self.alive = True
        self.name = "AbstractModel"

    def is_alive(self):
        """ Returns whether model is running. """
        return self.alive

    def get_name(self):
        """ Returns the name of the current model. """
        return self.name

    def step(self):
        """ Advances the model one step. """
        return True


class Overseer(Model):
    """ Model for optimising higher level logistics networks. """

    def __init__(self):
        super().__init__()
        self.name = "Overseer"


class Architect(Model):
    """ Model for designing tight-packed, 'tall' sub-unit factory layouts. """

    def __init__(self):
        super().__init__()
        self.name = "Architect"


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
