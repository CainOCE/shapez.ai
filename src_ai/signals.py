# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:46

@author: Cain Bruhn-Tanzer
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

class ListenServer:
    """ Generates a REST API server for the python backend. """

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self._routing()
        self.alive = False
        self.ryan = []

    def _routing(self):

        """Sets up the routes for the Flask app."""
        @self.app.route('/')
        def index_page_display():
            return Response(self.display_page(), mimetype='text/html')

        @self.app.route('/process', methods=['POST'])
        def on_data_received():
            return self.receive(request.json)

    def start(self):
        """Starts the Flask server."""
        self.alive = True
        self.app.run(debug=True)

    def display_page(self):
        """ Returns a HTML page when the python rest API is visited. """
        return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <title>Python Backend - Active</title>
            </head>
            <body>
                <h1>Status -> Active</h1>
            </body>
            </html>
            """

    def is_alive(self):
        """ Returns whether the Listen Server is running. """
        return self.alive

    def send(self):
        """ Emits a signal and data to be received by the game instance. """
        print("Not yet implemented.")

    def receive(self, data_in):
        """ Handles incoming signals sent by the game instance. """
        #print(data_in)
        if data_in and data_in.get("message") == "Hello":
            data_out = "World"
        else:
            data_out = "Unknown"
        self.ryan.append("miles")
        print(self.ryan)
        return jsonify({'move': data_out})  # The returned data


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
