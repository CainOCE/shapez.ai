# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25, 2024 at 13:00:32

@authors: Rhys Tyne, Cain Bruhn-Tanzer
"""
# A lot of unicode in this one, see below for suggestions.
# https://www.w3.org/TR/xml-entity-names/025.html
# http://xahlee.info/comp/unicode_arrows.html
# Note: Shapez.io defines rotation in True North Bearings e.g. URDL or NESW

EMPTY_TOKEN = '.'
UNKNOWN_TOKEN = "?"
BORDER_TOKENS = '◼◢◣◥◤'

TOKENS = {
    # Single Entity Structures
    "belt": "↑→↓←↗↘↙↖",
    "sender0": "⮉⮊⮋⮈",   # Underground belt entrance
    "receiver0": "⮉⮊⮋⮈",    # Underground belt exit
    "sender1": "⮉⮊⮋⮈",
    "receiver1": "⮉⮊⮋⮈",
    "miner": "▲▶▼◀",
    "rotator": "⮰⮱⮲⮳⮴⮵⮶⮷⮰⮱⮲⮳⮴⮵⮶⮷",  # 90 Right
    "rotatorCCW": "⮰⮱⮲⮳⮴⮵⮶⮷⮰⮱⮲⮳⮴⮵⮶⮷",   # CCW -> Counter Clockwise 90
    "rotator180": "⮰⮱⮲⮳⮴⮵⮶⮷⮰⮱⮲⮳⮴⮵⮶⮷",
    # "Merger": "╦╣╩╠",
    # "Splitter": "⬀⬂⬃⬁",   # Points to the ejection corner
    "trash": "X",
    "reader": '0',

    # Structures
    "hub": [
        "╔HUB",
        "║  ║",
        "║  ║",
        "╚══╝"
    ],
    "balancer": "⮤⮥⮣⮡⮦⮧⮠'⮢",
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
        self.map = {}

        # Get each chunk pos and use it as a key
        self.map = {}
        chunks = [] if chunks is None else chunks
        for chunk in chunks:
            key = f"{chunk.x}|{chunk.y}"
            self.map[key] = chunk

    def __str__(self):
        """ Representation when the game class is used as a string. """
        # TODO Give a brief description of the current goal.
        out = f"GAME: [{self.seed}] - LVL {self.level} - GOAL: [TBD]\n"
        return out

    # TODO:  Assumes valid gameState, may need a guard/validation function
    def update(self, game_state):
        """ Updates the python gameState to match client. """
        print("Incoming Python Update ->:")

        # 1.  Import Seed
        if self.seed is None:
            self.seed = game_state['seed']

        # 2.  Import Current Level and Goals
        if self.level is None:
            self.level = game_state['level']
        if self.goal is None:
            self.goal = game_state['goal']

        # 3.  Import Map Chunks
        for chunk in game_state['map']:
            c = game_state['map'][chunk]
            self.map[chunk] = Chunk(c['x'], c['y'])

            # for child in val:
            #     print(child)

        # 4.  Import Entities
        c = TOKENS
        for e in game_state['entities']:
            print(e)
            # Select Token based on entity
            token = UNKNOWN_TOKEN

            # TODO I hate this, its hacky and needs a better system.
            if e['type'] == "hub":
                self._place_structure(e['x'], e['y'], 0, 0, c["hub"])

            if e['type'] == "belt":
                if e['direction'] == 'top':
                    token = c["belt"][e['rotation']//90]
                if e['direction'] == 'right':
                    token = c["belt"][(e['rotation']//90)+4]
                if e['direction'] == 'left':
                    token = c["belt"][([7, 4, 5, 6])[e['rotation']//90]]
                self._place_token(e['x'], e['y'], token)

            if e['type'] == "miner":
                self._place_token(e['x'], e['y'], c["miner"][e['rotation']//90])

            if e['type'] == "balancer":
                if e['rotation'] == 0:
                    self._place_token(e['x']+0, e['y']+0, c["balancer"][0])
                    self._place_token(e['x']+1, e['y']+0, c["balancer"][1])
                if e['rotation'] == 90:
                    self._place_token(e['x']+0, e['y']+0, c["balancer"][2])
                    self._place_token(e['x']+0, e['y']+1, c["balancer"][3])
                if e['rotation'] == 180:
                    self._place_token(e['x']+0, e['y']+0, c["balancer"][4])
                    self._place_token(e['x']-1, e['y']+0, c["balancer"][5])
                if e['rotation'] == 270:
                    self._place_token(e['x']+0, e['y']+0, c["balancer"][6])
                    self._place_token(e['x']+0, e['y']-1, c["balancer"][7])
        return

    def get_chunk(self, x, y):
        """ Returns a chunk given a positional key. """
        key = f"{x}|{y}"
        return self.map.get(key)

    def list_chunks(self):
        """ Lists all chunks stored in the game class. """
        if not self.map:
            return "Current Chunks:  [None]\n"
        chunks = "\n".join(f"  {repr(chunk)}" for chunk in self.map)
        return f"Current Chunks:  \n{chunks}"

    def _get_token(self, x, y, token):
        """ Sets the Entity located at a global (x, y) coordinate. """
        (self.get_chunk(x // 16, y // 16)).place_token(x % 16, y % 16, token)

    def _place_token(self, x, y, token):
        """ Places a token at a global (x, y) coordinate. """
        (self.get_chunk(x // 16, y // 16)).place_token(x % 16, y % 16, token)

    def _place_structure(self, x, y, u, v, structure):
        """
        Places a structure at a global coordinate (x, y)
        with offset (u, v).
        """
        print(f"Placing structure: {structure} at ({x}, {y}) += ({u}, {v})")
        for j, row in enumerate(structure):
            for i, char in enumerate(row):
                if char != ' ':
                    self._place_token(x+i, y+j, char)

    def _rotate_structure(self, structure, rotation=0):
        """ Rotate a model structure by a rotation of 0, 90, 180, 270. """

        def clockwise(array):
            """ Rotate the model structure 90 degrees clockwise."""
            return [''.join(reversed(col)) for col in zip(*array)]

        def counterclockwise(array):
            """ Rotate the modelstructure 90 degrees counterclockwise."""
            return [''.join(col) for col in reversed(list(zip(*array)))]

        if rotation == 0:
            return structure
        elif rotation == 90:
            return clockwise(structure)
        elif rotation == 180:
            return clockwise(clockwise(structure))
        elif rotation == 270:
            return counterclockwise(structure)
        else:
            raise ValueError("Rotation must be 0, 90, 180, or 270 degrees.")

    def get_entities(self):
        """ Generate a list of entities for each token. """
        return

    def show_hub_area(self):
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
            self.get_chunk(-1, -1).display(),
            self.get_chunk(0, -1).display()
        )
        out += '\n'
        out += merge_output(
            self.get_chunk(-1, 0).display(),
            self.get_chunk(0, 0).display()
        )
        return out


class Chunk:
    """ Defines the chunk as a 16x16 collection of Tokens. """
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        self.width, self.height = 16, 16
        self.tokens = [
            [EMPTY_TOKEN for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def __repr__(self):
        """ Representation when the chunk is named by the console. """
        return f"{self.x}|{self.y}"

    def __str__(self, out=""):
        """ Representation when the chunk is used as a string. """
        return self.display()

    def place_token(self, x, y, token):
        """ Sets the token located at a chunk local (x, y) coordinate. """
        self.tokens[y][x] = token

    def get_token(self, x, y):
        """ Gets the token located at a chunk local (x, y) coordinate. """
        return self.tokens[y][x]

    def display(self, out=""):
        """ Representation with additional helper information.  """
        bt = BORDER_TOKENS

        def hval(x):
            """ Simple helper that returns a formatted hex number. """
            return hex(x)[2:].upper()

        # Generate a title line with padded border
        title = f"Chunk {str(self.x).rjust(3)}|{str(self.y).ljust(3)}"
        header = f"{bt[1]} {f"{bt[0]} "*7} {title} {f" {bt[0]}"*7} {bt[2]}\n"

        # Pretty Hex Column Header
        out += f"{bt[0]}  " + "".join(
            [f"{'   ' if x % 4 == 0 else ' '}" + hval(x) for x in range(0, 16)]
            ) + f"   {bt[0]}\n"

        # Some Spacers for clarity
        row_spacer = f"{bt[0]} {40*' '}    {bt[0]}\n"
        col_spacer = '   '

        # Generate Terminal Grid Representation
        for y, row in enumerate(self.tokens):
            out += row_spacer if (y > 0 and y % 4 == 0) else ''  # Spacing
            for x, val in enumerate(row):
                out += f"{bt[0]}  {hval(y)} " if x == 0 else ''  # Row Hex
                out += col_spacer if (x > 0 and x % 4 == 0) else ' '  # Spacing
                out += val  # Print Value at Point
            out += f"   {bt[0]}\n"  # Print Value at Point

        # Footer Border
        footer = f"{bt[3]}{22*f' {bt[0]}'} {bt[4]}"
        return f"{header}{out}{footer}"


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
