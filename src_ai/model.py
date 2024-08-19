# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:41

@author: Cain Bruhn-Tanzer
"""


class Overseer:
    """ Hello World """

    def __init__(self):
        self.alive = True

    def is_alive(self):
        """ Returns whether model is running. """
        return self.alive

    def step(self):
        """ Returns whether model is running. """
        return True


class Architect:
    """ Hello World """

    def __init__(self):
        self.alive = True

    def is_alive(self):
        """ Returns whether model is running. """
        return self.alive

    def step(self):
        """ Returns whether model is running. """
        return True


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
