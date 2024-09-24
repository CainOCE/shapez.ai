# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:35

@authors: Cain Bruhn-Tanzer, Rhys Tyne
"""

# TEMP:  Correct module imports for subfolder structure src_ai/app.py
import sys
import os
from signals import ListenServer
from model import Map, Chunk
from model import Overseer, Architect, RhysArchitect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    print("Running the Shapez.ai module...")

    # Start our AI Model Classes
    overseer = Overseer()
    architect = Architect()
    for model in [overseer, architect]:
        STATE = 'Active' if model.is_alive() else 'Inactive'
        print(f"{model.get_name()} is {STATE}")

    # Make a simple chunk
    test = Chunk(x=0, y=0, width=16, height=16)
    test.setTileXY(4, 4, 'O')
    test.setTileXY(2, 2, 'G')

    # Add it to the map
    board = Map([test])

    # Retrieve it from the map
    c = board.getChunk(0, 0)
    print(c)

    # Test the model merges (Ryhs Model -> Architect)
    # architect.train()

    # Test our Send and Receive Functions
    # sigs = ListenServer()
    # sigs.start()
    # sigs.send()
