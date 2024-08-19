# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:35

@author: Cain Bruhn-Tanzer
"""

# TEMP:  Correct module imports for subfolder structure src_ai/app.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from signals import send, receive
from model import Overseer, Architect

if __name__ == "__main__":
    print("Running the Shapez.ai module...\n")

    # Start our AI Model Classes
    overseer_ai = Overseer()
    architect_ai = Architect()

    # Test our Send and Receive Functions
    send()
    receive()
