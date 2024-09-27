# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20, 2024 at 13:35:38

@author: Cain Bruhn-Tanzer
"""

from src_ai.model import Architect


def test_miner_placement():
    """ Can the AI place a miner? """
    model = Architect()

    scenario = [
        'A'
    ]
    solutions = [
        None
    ]
    assert model.query(scenario) in solutions


if __name__ == "__main__":
    print("Please call this module from the test suite.")
