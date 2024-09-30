# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:35

@authors: Cain Bruhn-Tanzer, Rhys Tyne
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from game import GameState
from model import Overseer, Architect


class ShapezAI(Flask):
    """ App built atop FLASK to provide a REST API for the python backend. """
    def __init__(self):
        super().__init__(__name__)
        CORS(self)
        self._routing()

        self.game = GameState()
        self.overseer = Overseer()
        self.architect = Architect()

    def _routing(self):
        """Sets up the routes for the Flask app."""

        @self.route('/query_model', methods=['POST'])
        def on_query():
            """ Handles incoming queries sent by the game instance. """
            # Update GameState and Query Overseer
            self.game.update(request.json)
            response = self.overseer.query(request.json)
            return jsonify(response)


if __name__ == "__main__":
    print("Running the Shapez.ai module...")
    app = ShapezAI()
    app.run(debug=False)
