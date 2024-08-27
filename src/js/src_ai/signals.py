# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:46

@author: Cain Bruhn-Tanzer
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

incomes = [
    { 'description': 'salary', 'amount': 5000 }
]


@app.route('/incomes')
def get_incomes():
    return jsonify(incomes)


@app.route('/incomes', methods=['POST'])
def add_income():
    incomes.append(request.get_json())
    return '', 204


class ListenServer:
    """ Generates a REST API server for the python backend. """

    def __init__(self):
        self.alive = True

    def is_alive(self):
        """ Returns whether the Listen Server is running. """
        return self.alive

    def send(self):
        """ Emits a signal and data to be received by the game instance. """
        print("Not yet implemented.")

    def receive(self):
        """ Handles incoming signals sent by the game instance. """
        print("Not yet implemented.")


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
