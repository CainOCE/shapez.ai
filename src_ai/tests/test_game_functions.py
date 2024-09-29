# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20, 2024 at 13:35:38

@author: Cain Bruhn-Tanzer
"""

from src_ai.game import GameState


def test_rotate_structures():
    """ Can I rotate a structure arbitrarily? """
    game = GameState()

    structure = [
        "ABCD",
        "EFGH",
        "IJKL",
        "MNOP"
    ]
    structure90 = [
        "MIEA",
        "NJFB",
        "OKGC",
        "PLHD"
    ]
    structure180 = [
        "PONM",
        "LKJI",
        "HGFE",
        "DCBA"
    ]
    structure270 = [
        "DHLP",
        "CGKO",
        "BFJN",
        "AEIM"
    ]

    # Right Side Rotations
    # pylint: disable=W0212
    assert game._rotate_structure(structure, 90) == structure90
    assert game._rotate_structure(structure, 180) == structure180
    assert game._rotate_structure(structure, 270) == structure270
    # pylint: enable=all


if __name__ == "__main__":
    print("Please call this module from the test suite.")
