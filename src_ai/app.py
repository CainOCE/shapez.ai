# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:35

@authors: Cain Bruhn-Tanzer, Rhys Tyne
"""

# TEMP:  Correct module imports for subfolder structure src_ai/app.py
import sys
import os
from signals import ListenServer
from model import Board, Overseer, Architect
# from model import rhys_model
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    print("Running the Shapez.ai module...")

    # Start our AI Model Classes
    overseer_ai = Overseer()
    architect_ai = Architect()
    for model in [overseer_ai, architect_ai]:
        STATE = 'Active' if model.is_alive() else 'Inactive'
        print(f"{model.get_name()} is {STATE}")

    # Make a simple Board
    board = Board(5, 5)
    board.setTileXY(4, 4, 'O')
    board.setTileXY(2, 2, 'G')
    print(board)


    # TODO:  Test and merge the rhys_model
    # rhys_model()

    # Test our Send and Receive Functions
    # sigs = ListenServer()
    # sigs.start()
    # sigs.send()
