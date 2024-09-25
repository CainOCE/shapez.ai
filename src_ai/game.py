# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25, 2024 at 13:00:32

@authors: Rhys Tyne, Cain Bruhn-Tanzer
"""
# pylint: disable=C0103, C0209
# TODO:  Discuss suppressing error codes
#  C0103 -> snake case: TODO Debate this one
#  C0209 -> f_strings:  It's wrong here.

# A lot of uniode in this one, see below for suggestions.
# https://www.w3.org/TR/xml-entity-names/025.html
# http://xahlee.info/comp/unicode_arrows.html
# Note: Shapez.io defines rotation in True North Bearings

# Set some program output defaults
DEFAULT_TILES = '.'
UNKNOWN_TILE = "?"
BORDER_TILES = '◼◢◣◥◤'

# Entity Tile Map
ENTITIES = {
    # Resources
    "Red": "R",
    "Green": "G",
    "Blue": "B",

    # Entities
    "Belt": "↑→↓←↗↘↙↖",
    "Miner": "▲▶▼◀",
    "Rotator": "",
    "Merger": "",
    "Splitter": "",
    "Tunnel": "",
    "Trash": "X"
}
LEFT_ROTATOR_TILES = '⮰⮱⮲⮳⮴⮵⮶⮷⮰⮱⮲⮳⮴⮵⮶⮷'
RIGHT_ROTATOR_TILES = '⮰⮱⮲⮳⮴⮵⮶⮷⮰⮱⮲⮳⮴⮵⮶⮷'

# Entity Unicode Mapping
# Note:
Tiles = {
    # Resources
    "Red": "R",
    "Green": "G",
    "Blue": "B",

    # Single Entity Structures
    "Belt": "↑→↓←↗↘↙↖",
    "Miner": "▲▶▼◀",
    "Rotator": "",
    "Merger": "",
    "Splitter": "",
    "Tunnel": "",
    "Trash": "X",

    # 'Type': # ['Tile', URDL']
    "Balancer": "⤧⤨⤩⤪",
    "Cutter": ["⭻⭼⭽⯬"],
    "Stacker": ["◰◳◲◱"],
    "Mixer": ["◴◶◷◵"],
    "Painter": "",
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
        out += "GAME({self.seed})\n"
        return out

    # TODO:  Assumes valid gameState, may need a guard/validation function
    def update(self, incomingGameState):
        """ Updates the python gameState to match client. """
        print("Incoming Python Update ->:")

        # 1.  Import Seed
        if self.seed is None:
            self.seed = incomingGameState['seed']

        # 2.  Import Current Level and Goals
        if self.level is None:
            self.level = incomingGameState['level']
        if self.goal is None:
            self.goal = incomingGameState['goal']

        # 3.  Import Map Chunks
        for chunk in incomingGameState['map']:
            c = incomingGameState['map'][chunk]
            self.map[chunk] = Chunk(c['x'], c['y'])

            # for child in val:
            #     print(child)

        # 4.  Import Entities
        E = ENTITIES
        for e in incomingGameState['entities']:
            # Select Tile based on entity
            tile = UNKNOWN_TILE
            if e['type'] == "Belt":
                if e['direction'] == 'top':
                    tile = E["Belt"][e['rotation'] // 90]
                if e['direction'] == 'right':
                    tile = E["Belt"][(e['rotation'] // 90)+4]
                if e['direction'] == 'left':
                    if e['rotation'] == 0:
                        tile = E["Belt"][7]
                    if e['rotation'] == 90:
                        tile = E["Belt"][4]
                    if e['rotation'] == 180:
                        tile = E["Belt"][5]
                    if e['rotation'] == 270:
                        tile = E["Belt"][6]

            if e['type'] == "Miner":
                tile = E["Miner"][e['rotation'] // 90]

            self.setTileXY(e['x'], e['y'], tile)
        print(self.getChunk(0, 0))

    def getChunk(self, x, y):
        """ Returns a chunk given a positional key. """
        key = f"{x}|{y}"
        return self.map.get(key)

    def listChunks(self):
        """ Lists all chunks stored in the game class. """
        if not self.map:
            return "Current Chunks:  [None]\n"
        chunks = "\n".join(f"  {repr(chunk)}" for chunk in self.map)
        return f"Current Chunks:  \n{chunks}"

    def setTileXY(self, x, y, tile):
        """ Sets the tile located at a global (x, y) coordinate. """
        (self.getChunk(x // 16, y // 16)).setTileXY(x % 16, y % 16, tile)

    def getTileXY(self, x, y):
        """ Gets the tile located at a global (x, y) coordinate. """
        return (self.getChunk(x // 16, y // 16)).getTileXY(x % 16, y % 16)


class Chunk:
    """ Defines the chunk as a 16x16 collection of Tiles. """
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        self.width, self.height = 16, 16
        self.contents = [
            [DEFAULT_TILES[0] for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def __repr__(self):
        """ Representation when the chunk is named by the console. """
        return f"{self.x}|{self.y}"

    def __str__(self, out=""):
        """ Representation when the chunk is used as a string. """
        # return "\n".join("".join(row) for row in self.contents)
        return self.display()

    def setTileXY(self, x, y, tile):
        """ Sets the tile located at a chunk local (x, y) coordinate. """
        self.contents[y][x] = tile

    def getTileXY(self, x, y):
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
