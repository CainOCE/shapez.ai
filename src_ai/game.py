# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25, 2024 at 13:00:32

@authors: Rhys Tyne, Cain Bruhn-Tanzer
"""
# A lot of unicode in this one, see below for suggestions.
# https://www.w3.org/TR/xml-entity-names/025.html
# http://xahlee.info/comp/unicode_arrows.html
# Note: Shapez.io defines rotation in True North Bearings e.g. URDL or NESW

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
    "balancer": "1234",
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
    def __init__(self, chunks=None):
        # General Game State Information
        self.seed = None
        self.level = None
        self.goal = None

        # ECS Syle Lists
        self.entities = {}
        self.chunks = []
        self.resources = {}

    def __str__(self):
        """ Representation when the game class is used as a string. """
        # TODO Give a brief description of the current goal.
        out = f"GAME: [{self.seed}] - LVL {self.level} - GOAL: [TBD]\n"
        out += f"  - {len(self.entities)} Currnet Entities\n"
        out += f"  - {len(self.chunks)} Active Chunks\n"
        out += f"  - {len(self.resources)} Visible Resource Tiles"
        return out

    def import_game_state(self, game_state):
        """ Imports the ECS Entities from the frontend gamestate
            and assigns tokens or structures to them for the
            model to process. """

        # 1.  Import Seed & Active ChunkIDs
        if self.seed is None:
            self.seed = game_state['seed']
        self.chunks = game_state['map'].keys()

        # 2.  Import Current Level and Goals
        if self.level is None:
            self.level = game_state['level']
        if self.goal is None:
            self.goal = game_state['goal']

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
            if e['type'] in STRUCTS:
                if e['type'] == "hub":
                    e['token'] = "H"
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
        for id, chunk in game_state['map'].items():
            X, Y = map(int, id.split('|'))
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

    def get_chunk(self, X=0, Y=0):
        """ Returns the array output for a given chunk. """
        # Construct an empty grid to hold our tokens
        tokens = [[EMPTY_TOKEN for _ in range(16)] for _ in range(16)]

        # Filter resources within the chunk bounddaries
        local_resources = {}
        for uid, resource in self.resources.items():
            if resource["chunk_x"] == X and resource["chunk_y"] == Y:
                # Add Resources to the local list
                local_resources[uid] = resource

                # Add resource token to grid with colour
                token = resource["token"]
                token = f"{TERM_COLOUR[token]}{token}{TERM_COLOUR_RESET}"
                tokens[resource["local_y"]][resource["local_x"]] = token

        # Filter entities within the chunk boundaries
        local_entities = {}
        for uid, entity in self.entities.items():
            if entity["chunk_x"] == X and entity["chunk_y"] == Y:
                # Add Entities to the local list
                local_entities[uid] = entity

                # Add resource token to grid
                tokens[entity["local_y"]][entity["local_x"]] = entity["token"]

        return tokens

    def display_chunk(self, X=0, Y=0, out=""):
        """ Chunk representation with additional highlights and display. """
        tokens = self.get_chunk(X, Y)

        # Helper Function and Constants
        def hval(x):
            """ Simple helper that returns a formatted hex number. """
            return hex(x)[2:].upper()
        bt = BORDER_TOKENS

        # Generate a title line with padded border
        title = f"Chunk {str(X).rjust(3)}|{str(Y).ljust(3)}"
        header = f"{bt[1]} {f"{bt[0]} "*7} {title} {f" {bt[0]}"*7} {bt[2]}\n"

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

    def display_hub(self):
        """ Shows the chunks around the hub area. """
        # Split the strings into lines
        def merge_output(str1, str2):
            """ Merges two output statements. """
            merged_lines = []

            lines1 = str1.splitlines()
            lines2 = str2.splitlines()
            max_lines = max(len(lines1), len(lines2))

            for i in range(max_lines):
                line1 = lines1[i] if i < len(lines1) else ''
                line2 = lines2[i] if i < len(lines2) else ''

                # Merge the lines with the separator
                merged_lines.append(line1 + " " + line2)
            return '\n'.join(merged_lines)

        out = merge_output(
            self.display_chunk(-1, -1),
            self.display_chunk(0, -1)
        )
        out += '\n'
        out += merge_output(
            self.display_chunk(-1, 0),
            self.display_chunk(0, 0)
        )
        return out

    def list_chunks(self):
        """ Lists all chunks stored in the game class. """
        if not self.chunks:
            return "Current Chunks:  [None]\n"
        chunks = "\n".join(f"  {chunk}" for chunk in self.chunks)
        return f"Current Chunks:  \n{chunks}"

    # def _get_token(self, x, y):
    #     """ Gets the Entity located at a global (x, y) coordinate. """
    #     # TODO:  There should only be one.
    #     return None

    # def _place_resource(self, x, y, resource):
    #     """ Colours the tile based on the available resources. """
    #     if resource in "rgb":
    #         self._place_token(x, y, resource)

    # def _place_token(self, x, y, token):
    #     """ Places a token at a global (x, y) coordinate. """
    #     (self.get_chunk(x // 16, y // 16)).place_token(x % 16, y % 16, token)

    # def _place_structure(self, x, y, u, v, structure):
    #     """
    #     Places a structure at a global coordinate (x, y)
    #     with offset (u, v).
    #     """
    #     print(f"Placing structure: {structure} at ({x}, {y}) += ({u}, {v})")
    #     for j, row in enumerate(structure):
    #         for i, char in enumerate(row):
    #             if char != ' ':
    #                 self._place_token(x+i, y+j, char)

    # def _rotate_structure(self, structure, rotation=0):
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


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
