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
        "║  ║",
        "║  ║",
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
    """ Defines the gameState object in a form malleable my an AI Model.  """
    def __init__(self):
        # General Game State Information
        self.seed = None
        self.level = None
        self.goal = None

        # ECS Syle Lists
        self.entities = {}
        self.chunks = []
        self.resources = {}
        self.empties = [] # rhys made array
        self.size = 32 # some size factor which the model only focusing on that area
        # so 32 x 32 grid around the hub for example 
    


    def __str__(self):
        """ Representation when the game class is used as a string. """
        # TODO Give a brief description of the current goal.
       # goal_desc = f"'{self.goal["item"]}' ({self.goal["amount"]})"
        goal_desc = 'a'
        out = f"GAME[seed={self.seed}]: LVL {self.level} -> {goal_desc}\n"
        out += f"  - {len(self.entities)} Current Entities\n"
        out += f"  - {len(self.chunks)} Active Chunks\n"
        out += f"  - {len(self.resources)} Visible Resource Tiles"
        return out

    def get_seed(self):
        """ Returns the game seed in play. """
        return self.seed

    def get_all_actions(self):
        """ Returns the action space of the current GameState. """
        # TODO Implement Action Space Calculation.

        # rhys thoughts: make level limit number of actions available
        ### need to implement this
        ###

        #
        #
        return ["↑", "→"]
    
    def get_building_actions(self, building):
        actions = TOKENS.get('belt').split() + TOKENS.get('beltCnrR').split() + TOKENS.get('beltCnrL').split() 
        actions.remove(building)
        #actions.append('0') ## delete???
        return actions

    def get_empty_actions(self):
        # return all possible buidlings to place on an empty square
        return TOKENS.get('belt').split() + TOKENS.get('beltCnrR').split() + TOKENS.get('beltCnrL').split() 
    
    # get available actions for resource cell
    def get_resource_actions(self):
        return TOKENS.get('miner').split()
    
    def step(self, index, action):
        i = index % self.size
        j = index // self.size
        # update ECS arrays

        ## this bit is assuming you can replace building maybe implement later
        if (i,j) in self.entities.keys(): # idk if this is right format?
            if action == 'delete':
                self.entities.pop((i, j))
            else:
                # replace entity with new building
                pass
        elif (i,j) in self.resources.keys():
            self.entities[(i, j)] = action

        else: # cell must be empty
            self.empties.remove((i, j))
            self.entities[(i, j)] = action

        # send action to API????? ---- leaveing this to Cain



        # apply heuristic, 
        # I assume we only need entities, goals and resources for this:
        return self.evaluate_state()
        

    # still needs adjust ing for weird strings
    def get_possible_actions(self):
        # gonna do this in naive way -- sorry Cain
        
        state = self.get_region()
        actions = []
        # index = i + size + j

        for i in range(len(state)):
            for j in range(len(state[0])):
                index = i * len(state) + j
                cell = state[i,j]
                # need to reqrite these with value retuned by get_region
                if cell == "HUB":  
                    pass
                elif cell == "empty":
                    actions[index] = self.get_empty_actions()

                elif cell == "resource":
                    actions[index] = self.get_resource_actions()

        return actions


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

        # 3.  Import Game entities
        for uid, e in game_state['entities'].items():
            # GUARD:  Entity already exists on the backend
            if uid in self.entities:
                continue

            # Add some positional information to the entity
            e["local_x"] = e["x"] % 16
            e["local_y"] = e["y"] % 16
            e["chunk_x"] = e["x"] // 16
            e["chunk_y"] = e["y"] // 16

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

            # Handle Structure Entities
            struct = UNKNOWN_TOKEN
            e['struct'] = token
            if e['type'] in STRUCTS:
                if e['type'] == "hub":
                    e['token'] = "H"
                    struct = STRUCTS["hub"]
                # self._place_structure(e['x'], e['y'], 0, 0, TOKENS["hub"])
                if e['type'] == "balancer":
                    if e['rotation'] == 0:
                        struct = STRUCTS["balancer"][0]
                    if e['rotation'] == 90:
                        struct = STRUCTS["balancer"][2]
                    if e['rotation'] == 180:
                        struct = STRUCTS["balancer"][4]
                    if e['rotation'] == 270:
                        struct = STRUCTS["balancer"][6]
                e['struct'] = struct
                # TODO Think on the above section

            # Commit Entity
            self.entities[uid] = e

        # 3b. Remove all 'dead' entities.
        for uid in list(self.entities.keys()):
            if uid not in game_state['entities'].keys():
                del self.entities[uid]

        # 4.  Import all resources
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

    def get_region(self, x=0, y=0, width=16, height=16, buffer=8):
        """ Returns an arbitrary square region of the game board. """
        xmin, xmax = (x-buffer, x+width+buffer)
        ymin, ymax = (y-buffer, y+height+buffer)
        x_range, y_range = (range(xmin, xmax), range(ymin, ymax))

        # Empty grid to hold our tokens with a buffer region for structure gen
        tokens = [[EMPTY_TOKEN for _ in x_range] for _ in y_range]

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

    def display_region(self, x=0, y=0, width=16, height=16, buffer=5):
        """ Creates a neatly displayed region graphic. """
        tokens = self.get_region(x, y, width, height, buffer)
        return "\n".join(["".join(row) for row in tokens])

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
