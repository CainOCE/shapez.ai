# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:35

@authors: Cain Bruhn-Tanzer, Ryan Miles, Shannon Searle, Rhys Tyne
"""
import logging
import time
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from game import GameState
from model import Overseer, Architect

# Suppress Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)


class ShapezAI(Flask):
    """ App built atop FLASK to provide a REST API for the python backend """
    def __init__(self):
        super().__init__(__name__)
        CORS(self)
        self._routing()

        self.game = GameState()
        self.overseer = Overseer()
        self.architect = Architect()
        self.t0 = time.time()

    def _routing(self):
        """Sets up the routes for the Flask app."""

        @self.route('/ping', methods=['POST'])
        def on_ping():
            return jsonify(self.architect.get_state_machine())

        @self.route('/query', methods=['POST'])
        def on_query():
            """ Handles incoming queries sent by the game instance. """

            # Log Query
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] -> Model Query:")

            # Update GameState
            self.game.import_game_state(request.json)
            print(self.game)

            # Query Overseer
            #response = self.overseer.query(self.game)

            # query architect
            response = self.architect.query(self.game)

            # Show a nice output to us after a query.
            print(self.game.display_region_info(-18, -18, 36, 36))

            return jsonify(response)

        @self.route('/train', methods=['POST'])
        def on_train():
            """ Handles incoming training requests sent by the game instance.
            """
            pre_state = self.architect.get_state_machine()

            # Log Query
            if pre_state == "ONLINE":
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[{current_time}] -> Training Request:")

            # Update GameState
            self.game.import_game_state(request.json)

            # Train the Architect Model
            response = {
                'action': self.architect.train(self.game),
                'state': self.architect.get_state_machine(),
                'status': self.architect.get_training_status(),
            }

            return jsonify(response)


if __name__ == "__main__":
    print("Running the Shapez.ai module...")
    app = ShapezAI()
    app.run(debug=False)
