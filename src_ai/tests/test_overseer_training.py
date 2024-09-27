# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20, 2024 at 13:35:38

@author: Cain Bruhn-Tanzer
"""

from src_ai.model import Overseer


def test_belt_pathing_2x2():
    """ Can the AI draw a minimal path from an occupied A to B? """
    model = Overseer()
    scenario = [
        ['A', '.', 'B'],
    ]
    solutions = [
        None,
        ['A', '→', 'B'],
    ]
    assert model.query(scenario) in solutions


def test_belt_pathing_3x3():
    """ Can the model perform in a multi-choice scenario? """
    model = Overseer()
    scenario = [
        ['A', '.', '.',],
        ['.', '.', '.',],
        ['.', '.', 'B',],
    ]
    solutions = [
        None,
        # TODO How do we solve this instance?
    ]
    assert model.query(scenario) in solutions


def test_underground_belt_pathing_1x5():
    """ Can the AI play an underground belt? """
    model = Overseer()
    scenario = [
        ['A', '.', 'X', '.', 'B'],
    ]
    solutions = [
        None,
        ['A', '⮊', 'X', '⮈', 'B'],
    ]
    assert model.query(scenario) in solutions


if __name__ == "__main__":
    print("Please call this module from the test suite.")
