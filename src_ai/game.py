# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25, 2024 at 13:00:32

@authors: Rhys Tyne, Cain Bruhn-Tanzer
"""
# A lot of unicode in this one, see below for suggestions.
# https://www.w3.org/TR/xml-entity-names/025.html
# http://xahlee.info/comp/unicode_arrows.html
# Note: Shapez.io defines rotation in True North Bearings e.g. URDL or NESW

EMPTY_TILE = '.'
UNKNOWN_TILE = "?"
BORDER_TILES = '◼◢◣◥◤'

ENTITIES = {
    # Resources
    "Red": "R",
    "Green": "G",
    "Blue": "B",

    # Single Entity Structures
    "Belt": "↑→↓←↗↘↙↖",
    "Miner": "▲▶▼◀",
    "RotatorL": "⮰⮱⮲⮳⮴⮵⮶⮷⮰⮱⮲⮳⮴⮵⮶⮷",
    "RotatorR": "⮰⮱⮲⮳⮴⮵⮶⮷⮰⮱⮲⮳⮴⮵⮶⮷",
    "Merger": "╦╣╩╠",
    "Splitter": "╦╣╩╠",
    "Tunnel": "⮉⮊⮋⮈",
    "Trash": "X",
    "BeltReader": '0',

    # Structures
    "Hub": {
        "tile": 'X',
        "struct": [
            "╔HUB",
            "║  ║",
            "║  ║",
            "╚══╝"
            ],
    },
    "Balancer": ["⮤⮥", "⮣⮡ ", "⮦⮧", "⮠'⮢"],
    "DualCutter": ["⭻🠴"],
    "QuadCutter": ["⭻🠴🠴🠴"],
    "Stacker": ["◰🠴", "◳🠵", "◲🠶", "◱🠷"],
    "Mixer": ["◴🠴", "◷🠵", "◶🠶", "◵🠷"],
    "DualPainterL": ["⮙🠵", "??", "??", "??"],
    "DualPainterR": ["⮙🠵", "??", "??", "??"],
    "QuadPainterA": ["⮙🠵", "??", "??", "??"],
    "QuadPainterB": ["⮙🠵", "??", "??", "??"],
    "Storage": [
        ["S⇑",
         "╚╝"],
        ["╔S",
         "╚⇒"],
        ["╔╗",
         "⇓S"],
        ["⇐╗",
         "S╝"],
    ]

    # Wire Structures
    # TODO Wiring as an advanced goal? Separate map layer
}


class Game():
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

    def __str__(self, out=""):
        """ Representation when the game class is used as a string. """
        out += f"GAME: [{self.seed}] - LVL {self.level}\n"
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
        E = ENTITIES
        for e in game_state['entities']:
            # Select Tile based on entity
            tile = UNKNOWN_TILE

            if e['type'] == "Hub":
                self._place_structure(e['x'], ['y'], 0, 0, E["Hub"])

            if e['type'] == "Belt":
                if e['direction'] == 'top':
                    tile = E["Belt"][e['rotation']//90]
                if e['direction'] == 'right':
                    tile = E["Belt"][(e['rotation']//90)+4]
                if e['direction'] == 'left':
                    tile = E["Belt"][([7, 4, 5, 6])[e['rotation']//90]]
                self._place_tile(e['x'], e['y'], tile)

            if e['type'] == "Miner":
                self._place_tile(e['x'], e['y'], E["Miner"][e['rotation']//90])
        print(self)
        print(self.get_chunk(0, 0))

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

    def _get_tile(self, x, y, tile):
        """ Sets the Entity located at a global (x, y) coordinate. """
        (self.get_chunk(x // 16, y // 16)).place_tile(x % 16, y % 16, tile)

    def _place_tile(self, x, y, tile):
        """ Places a tile at a global (x, y) coordinate. """
        (self.get_chunk(x // 16, y // 16)).place_tile(x % 16, y % 16, tile)

    def _place_structure(self, x, y, u, v, structure):
        """
        Places a structure at a global coordinate (x, y)
        with offset (u, v).
        """
        print(f"NYIPlacing structure: {structure} at ({x}, {y}) += ({u}, {v})")


class Chunk:
    """ Defines the chunk as a 16x16 collection of Tiles. """
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        self.width, self.height = 16, 16
        self.contents = [
            [EMPTY_TILE for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def __repr__(self):
        """ Representation when the chunk is named by the console. """
        return f"{self.x}|{self.y}"

    def __str__(self, out=""):
        """ Representation when the chunk is used as a string. """
        # return "\n".join("".join(row) for row in self.contents)
        return self.display()

    def place_tile(self, x, y, tile):
        """ Sets the tile located at a chunk local (x, y) coordinate. """
        self.contents[y][x] = tile

    def get_tile(self, x, y):
        """ Gets the tile located at a chunk local (x, y) coordinate. """
        return self.contents[y][x]

    def display(self, out=""):
        """ Representation with additional helper information.  """
        BT = BORDER_TILES

        def hval(x):
            """ Simple helper that returns a formatted hex number. """
            return hex(x)[2:].upper()

        # Generate a title line with padded border
        title = f"Chunk {str(self.x).rjust(3)}|{str(self.y).ljust(3)}"
        header = f"{BT[1]} {f"{BT[0]} "*7} {title} {f" {BT[0]}"*7} {BT[2]}\n"

        # Pretty Hex Column Header
        out += f"{BT[0]}  " + "".join(
            [f"{'   ' if x % 4 == 0 else ' '}" + hval(x) for x in range(0, 16)]
            ) + f"   {BT[0]}\n"

        # Some Spacers for clarity
        ROW_SPACER = f"{BT[0]} {40*' '}    {BT[0]}\n"
        COL_SPACER = '   '

        # Generate Terminal Grid Representation
        for y, row in enumerate(self.contents):
            out += ROW_SPACER if (y > 0 and y % 4 == 0) else ''  # Spacing
            for x, val in enumerate(row):
                out += f"{BT[0]}  {hval(y)} " if x == 0 else ''  # Row Hex
                out += COL_SPACER if (x > 0 and x % 4 == 0) else ' '  # Spacing
                out += val  # Print Value at Point
            out += f"   {BT[0]} \n"  # Print Value at Point

        # Footer Border
        footer = f"{BT[3]}{22*f' {BT[0]}'} {BT[4]}"
        return f"{header}{out}{footer}"


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
