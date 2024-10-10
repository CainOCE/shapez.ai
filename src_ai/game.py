# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25, 2024 at 13:00:32

@authors: Rhys Tyne, Cain Bruhn-Tanzer
"""
# A lot of unicode in this one, see below for suggestions.
# https://www.w3.org/TR/xml-entity-names/025.html
# http://xahlee.info/comp/unicode_arrows.html
# Note: Shapez.io defines rotation in True North Bearings e.g. URDL or NESW

import numpy as np

TERM_COLOUR = {
    'r': "\033[41m",
    'g': "\033[42m",
    'b': "\033[44m",
    'X': "\033[48;5;237m",
}
TERM_COLOUR_RESET = "\033[0m"

EMPTY = '.'
EMPTY_TOKEN = '.'
UNKNOWN_TOKEN = "?"
BORDER_TOKENS = '◼◢◣◥◤'

TOKENS = {
    # Single Entity Structures with Direction
    "belt": "↑→↓←",
    "beltCnrL": "↖↗↘↙",
    "beltCnrR": "↗↘↙↖",
    "sender0": "⮉⮊⮋⮈",   # Underground belt entrance
    "receiver0": "⮉⮊⮋⮈",    # Underground belt exit
    "sender1": "⮉⮊⮋⮈",
    "receiver1": "⮉⮊⮋⮈",
    "miner": "▲▶▼◀",
    "rotator": "⮰⮱⮲⮳",      # 90 Right
    "rotatorCCW": "⮰⮱⮲⮳",   # CCW -> Counter Clockwise 90
    "rotator180": "⮰⮱⮲⮳⮴",
    # "Merger": "╦╣╩╠",
    # "Splitter": "⬀⬂⬃⬁",   # Points to the ejection corner
    "trash": "TTTT",
    "reader": 'OOOO',
}

STRUCTS = {
    # Structures
    "hub": [
        "╔HUB",
        "║XX║",
        "║XX║",
        "╚══╝"
    ],
    # "balancer": "⮤⮥⮣⮡⮦⮧⮠'⮢",
    "balancer": ["⮤⮥", "⮣⮡", "⮦⮧", "⮠'⮢"],
    "cutter": ["⭻🠴"],
    "cutterQuad": ["⭻🠴🠴🠴"],
    "stacker": ["◰🠴", "◳🠵", "◲🠶", "◱🠷"],
    "mixer": ["◴🠴", "◷🠵", "◶🠶", "◵🠷"],
    "painter": ["⮙🠵", "??", "??", "??"],
    "painterDouble": ["⮙🠵", "??", "??", "??"],
    "painterQuad": ["⮙🠵", "??", "??", "??"],
    "storage": [
        ["S⇑",
         "╚╝"],
        ["╔S",
         "╚⇒"],
        ["╔╗",
         "⇓S"],
        ["⇐╗",
         "S╝"],
    ]

    # TODO Wire Structures as an advanced goal? Req. Separate map layer
}


class GameState():
    """ Defines the gameState object in a form malleable by an AI Model.  """
    def __init__(self):
        # General Game State Information
        self.seed = None
        self.level = None
        self.goal = None

        # ECS Syle Lists
        self.entities = {}
        self.resources = {}
        self.chunks = []
        self.storage = {}

    def __str__(self):
        """ Representation when the game class is used as a string. """
        goal_item, goal_amount = self.get_goal()
        goal_desc = f"\'{goal_item}\' ({goal_amount})"
        out = f"GAME[seed={self.seed}]: LVL {self.level} -> {goal_desc}\n"
        out += f"  - {len(self.entities)} Current Entities\n"
        out += f"  - {len(self.chunks)} Active Chunks\n"
        out += f"  - {len(self.resources)} Visible Resource Tiles"
        return out

    def get_seed(self):
        """ Returns the game seed in play. """
        return self.seed

    def get_goal(self):
        """ Returns a tuple containing the goal hash and amount required. """
        return (self.goal["item"], self.goal["amount"])

    def get_stored_amount(self, key):
        """ Returns the number of stored items of key in the game. """
        if key in self.storage.keys():
            return self.storage[key]
        return 0

    def get_actions(self):
        """ Returns a list of all actions in the current GameState. """
        return ''.join(TOKENS.values())

    def get_basic_actions(self):
        """ Returns a basic list of actions. """
        return ["belt"]

    def get_action_space(self, region=None):
        """ Returns the action space list. \n
        Note that this list must be one-hot.

            Returns:
                list: ["x|y|rot|type", ...]
        """
        region = region if region is not None else self.get_region_in_play()
        rotations = [0, 90, 180, 270]

        # Check each possible position in region
        action_space = []
        for y, row in enumerate(region):
            for x, token in enumerate(row):
                if token == EMPTY_TOKEN:
                    # If token at x|y is empty, add all token actions to it.
                    for rotation in rotations:
                        for action in self.get_basic_actions():
                            action_space.append(f"{x}|{y}|{rotation}|{action}")

                    # TODO Check if structure can fit at location. -- could we just overlap????


                if f"{x}|{y}" in self.resources.keys():
                    # if resource -- add action to place miner
                    # TODO - only allow rotations which send in HUB direction
                    for rotation in rotations:
                            action_space.append(f"{x}|{y}|{rotation}|miner")



        return action_space

    def import_game_state(self, game_state):
        """ Imports the ECS Entities from the frontend GameState
            and assigns tokens or structures to them for the
            model to process. """

        # 1.  Import Seed & Active ChunkIDs
        if self.seed is None or self.seed != game_state['seed']:
            self.seed = game_state['seed']
            self.entities = {}
            self.chunks = game_state['map'].keys()
            self.resources = {}

        # 1b. If Seed has changed nuke the chunks and resources
        if self.seed != game_state['seed']:
            self.chunks = []
            self.resources = {}

        # 2.  Import Current Level and Goals
        if self.level is None:
            self.level = game_state['level']
        if self.goal is None:
            self.goal = {
                'item': game_state["goal"]["definition"]["cachedHash"],
                'amount': game_state["goal"]['required']
            }

        # 3.  Import Current Storage Levels
        self.storage = game_state["storage"]

        # 4.  Import Game entities
        for uid, e in game_state['entities'].items():
            # GUARD:  Entity already exists on the backend
            if uid in self.entities:
                continue

            # Add some positional information to the entity
            e["local_x"] = int(e["x"]) % 16
            e["local_y"] = int(e["y"]) % 16
            e["chunk_x"] = int(e["x"]) // 16
            e["chunk_y"] = int(e["y"]) // 16

            # Single Token Entities
            token = UNKNOWN_TOKEN
            e['token'] = token
            if e['type'] in TOKENS:
                # Use the token in our TOKENS mapping
                token = TOKENS[e['type']][e['rotation']//90]

                # Special case of belt corners
                if e['type'] == "belt":
                    if e['direction'] == 'left':
                        token = TOKENS["beltCnrL"][e['rotation']//90]
                    if e['direction'] == 'right':
                        token = TOKENS["beltCnrR"][e['rotation']//90]
                e['token'] = token

            # Token Structured Entities
            struct = UNKNOWN_TOKEN
            e['struct'] = token
            if e['type'] in STRUCTS:
                if e['type'] == "hub":
                    e['token'] = "H"
                    struct = STRUCTS["hub"]
                if e['type'] == "balancer":
                    struct = STRUCTS["balancer"][2*(e['rotation']//90)]
                e['struct'] = struct
                # TODO Think on the above section

            # Commit Entity
            self.entities[uid] = e

        # 4b. Remove all 'dead' entities.
        for uid in list(self.entities.keys()):
            if uid not in game_state['entities'].keys():
                del self.entities[uid]

        # 5.  Import all resources
        for uid, chunk in game_state['map'].items():
            X, Y = map(int, uid.split('|'))
            for x, row in enumerate(chunk["resources"]):
                for y, val in enumerate(row):
                    # GUARD:  No empty tiles
                    if val is None:
                        continue

                    if val['_type'] == 'shape':
                        token = 'X'
                        value = val['definition']['cachedHash']

                    if val['_type'] == 'color':
                        token = val['color'][0]
                        value = val['color']

                    # Pack our resources into a list
                    self.resources[f"{X*16+x}|{Y*16+y}"] = {
                        "x": X*16+x, "y": Y*16+y,
                        "local_x": x, "local_y": y,
                        "chunk_x": X, "chunk_y": Y,
                        "token": token,
                        "type": val['_type'],
                        "value": value,
                    }

        return

    def get_region(self, x=0, y=0, width=16, height=16, buffer=5):
        """ Returns an arbitrary square region of the game board. """
        xmin, xmax = (x-buffer, x+width+buffer)
        ymin, ymax = (y-buffer, y+height+buffer)
        x_range, y_range = (range(xmin, xmax), range(ymin, ymax))

        # Empty grid to hold our tokens with a buffer region for structure gen
        tokens = [[EMPTY for _ in x_range] for _ in y_range]

        # Filter resources within the chunk bounddaries
        for _, resource in self.resources.items():
            if resource["x"] in x_range and resource["y"] in y_range:
                # Add resource token to grid with colour
                token = resource["token"]
                token = f"{TERM_COLOUR[token]}{token}{TERM_COLOUR_RESET}"
                tokens[resource["y"]-ymin][resource["x"]-xmin] = token

        # Filter entities within the chunk boundaries
        for _, entity in self.entities.items():
            if entity["x"] in x_range and entity["y"] in y_range:
                X, Y = (entity["x"]-xmin, entity["y"]-ymin)
                # Add the resource token to the grid
                tokens[Y][X] = entity["token"]

                # If the entity has a structure place it on the grid
                if entity["struct"] is not None:
                    for j, row in enumerate(entity["struct"]):
                        for i, char in enumerate(row):
                            if char != ' ':
                                tokens[Y+j][X+i] = char

        # Remove the buffered region and return
        return [row[buffer:-buffer] for row in tokens[buffer:-buffer]]

    def get_region_radial(self, x=0, y=0, radius=16):
        """ Returns an square region of the game board with given radius. """
        return self.get_region(x-radius, y-radius, 2*radius, 2*radius)

    def get_region_in_play(self):
        """ Returns an square region of the game board with given radius. """
        return self.get_region_radial(x=0, y=0, radius=16)
        

    def display_region(self, x=0, y=0, width=16, height=16, buffer=5):
        """ Creates a neatly displayed region graphic. """
        tokens = self.get_region(x, y, width, height, buffer)
        output = "\n".join(["".join(row) for row in tokens])
        return output.replace(EMPTY, EMPTY_TOKEN)

    def display_region_info(self, x=0, y=0, width=16, height=16, buffer=5):
        """ Creates a neatly displayed region graphic with additional
        information. """
        tokens = self.get_region(x, y, width, height, buffer)

        # 1.  Generate a spaced grid
        spaced_grid = "\n".join([" ".join(row) for row in tokens])
        title_bar = f"Region {x, y}".center(width*2)

        return f"{title_bar}\n{spaced_grid}"

    def display_chunk_info(self, X=0, Y=0, out=""):
        """ Chunk representation with additional highlights and display. """
        tokens = self.get_region(X*16, Y*16)

        # Helper Function and Constants
        def hval(x):
            """ Simple helper that returns a formatted hex number. """
            return hex(x)[2:].upper()
        bt = BORDER_TOKENS

        # Generate a title line with padded border
        title = f"Chunk {str(X).rjust(3)}|{str(Y).ljust(3)}"
        left, right = (f"{bt[0]} ", f" {bt[0]}")
        header = f"{bt[1]} {left*7} {title} {right*7} {bt[2]}\n"

        # Pretty Hex Column Header
        out += f"{bt[0]}  " + "".join(
            [f"{'   ' if x % 4 == 0 else ' '}" + hval(x) for x in range(0, 16)]
            ) + f"   {bt[0]}\n"

        # Some Spacers for clarity
        row_spacer = f"{bt[0]} {40*' '}    {bt[0]}\n"
        col_spacer = '   '

        # Generate Terminal Grid Representation
        for y, row in enumerate(tokens):
            out += row_spacer if (y > 0 and y % 4 == 0) else ''  # Spacing
            for x, val in enumerate(row):
                out += f"{bt[0]}  {hval(y)} " if x == 0 else ''  # Row Hex
                out += col_spacer if (x > 0 and x % 4 == 0) else ' '  # Spacing
                out += val  # Print Value at Point
            out += f"   {bt[0]}\n"  # Print Value at Point

        # Footer Border
        footer = f"{bt[3]}{22*f' {bt[0]}'} {bt[4]}"
        return f"{header}{out}{footer}"

    def list_chunks(self):
        """ Lists all chunks stored in the game class. """
        if not self.chunks:
            return "Current Chunks:  [None]\n"
        chunks = "\n".join(f"  {chunk}" for chunk in self.chunks)
        return f"Current Chunks:  \n{chunks}"

    # def _place_structure(self, structure, rotation=0):
    #     """ Rotate a model structure by a rotation of 0, 90, 180, 270. """

    #     def clockwise(array):
    #         """ Rotate the model structure 90 degrees clockwise."""
    #         return [''.join(reversed(col)) for col in zip(*array)]

    #     def counterclockwise(array):
    #         """ Rotate the modelstructure 90 degrees counterclockwise."""
    #         return [''.join(col) for col in reversed(list(zip(*array)))]

    #     if rotation == 0:
    #         return structure
    #     elif rotation == 90:
    #         return clockwise(structure)
    #     elif rotation == 180:
    #         return clockwise(clockwise(structure))
    #     elif rotation == 270:
    #         return counterclockwise(structure)
    #     else:
    #         raise ValueError("Rotation must be 0, 90, 180, or 270 degrees.")

    def validate(self):
        """ Validates a model solution with the game state and returns a
        score for the given solution. """
        return 0

if __name__ == "__main__":
    print("Please call this module as a dependency or import.")