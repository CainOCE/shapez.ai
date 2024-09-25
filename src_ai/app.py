# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:35

@authors: Cain Bruhn-Tanzer, Rhys Tyne
"""
import sys
import os
from game import Game, Chunk
from model import Overseer, Architect, RhysArchitect
from signals import ListenServer

# TODO:  Correct module imports for subfolder structure src_ai/app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    print("Running the Shapez.ai module...")

    # Start our AI Model Classes
    overseer = Overseer()
    architect = Architect()
    for model in [overseer, architect]:
        STATE = 'Active' if model.is_alive() else 'Inactive'
        print(f"{model.get_name()} is {STATE}")

    # Test the model merges (Rhys Model -> Architect)
    # architect.train()

    # Test our Send and Receive Functions
    sigs = ListenServer()
    sigs.start()
    sigs.send()
