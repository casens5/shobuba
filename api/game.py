import numpy as np
import re

from dataclasses import dataclass


@dataclass
class BoardMove:
    board: int
    origin: int
    destination: int = None


@dataclass
class Direction:
    cardinal: int
    length: int


@dataclass
class Move:
    passive: BoardMove
    active: BoardMove
    direction: Direction


class Game:
    def __init__(self):
        self.board = []
        self.initialize_board()
        self.playerTurn = "black"

    def initialize_board(self):
        self.board = [
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
        ]

    def pretty_print(self):
        value_to_symbol = {
            None: ".",
            1: "X",
            2: "O",
        }

        grids = [np.array(row).reshape(4, 4) for row in self.board]
        grid_layout = np.array(grids).reshape(2, 2, 4, 4)

        print()
        for row in grid_layout:
            for i in range(4):
                print(
                    "    ".join(
                        " ".join(value_to_symbol.get(cell, ".") for cell in grid[i])
                        for grid in row
                    )
                )
            print()

    def change_turn(self):
        if self.playerTurn == "black":
            self.playerTurn = "white"
        else:
            self.playerTurn = "black"

    def is_move_legal(self, move):
        if not move.passive.destination or not move.active.destination:
            print("move is out of bounds")
            return False

        if (
            move.passive.board == move.active.board
            or (move.passive.board == 0 and move.active.board == 3)
            or (move.passive.board == 1 and move.active.board == 2)
            or (move.passive.board == 2 and move.active.board == 1)
            or (move.passive.board == 3 and move.active.board == 0)
        ):
            print("active and passive moves can't be on the same color")
            return False

        if (self.playerTurn == "white" and move.passive.board < 2) or (
            self.playerTurn == "black" and move.passive.board > 1
        ):
            print("passive move must be in your home board")
            return False

        return True

    def get_move_destination(self, origin, direction, length):
        x = origin % 4
        y = origin // 4

        if direction == 7 or direction < 2:
            y -= length
        if direction > 2 and direction < 6:
            y += length
        if direction > 4:
            x -= length
        if direction > 0 and direction < 4:
            x += length

        if x < 0 or y < 0 or x > 3 or y > 3:
            return None
        else:
            return (y * 4) + x

    def parse_move(self, input_match):
        letter_to_index = {
            "a": 0,
            "b": 1,
            "c": 2,
            "d": 3,
        }

        cardinal_to_index = {
            "n": 0,
            "ne": 1,
            "e": 2,
            "se": 3,
            "s": 4,
            "sw": 5,
            "w": 6,
            "nw": 7,
        }

        groups = input_match.groups()
        move = Move(
            passive=BoardMove(
                board=letter_to_index.get(groups[0]),
                origin=int(groups[1]) - 1,
            ),
            active=BoardMove(
                board=letter_to_index.get(groups[4]),
                origin=int(groups[5]) - 1,
            ),
            direction=Direction(
                cardinal=cardinal_to_index.get(groups[2]),
                length=int(groups[3]),
            ),
        )

        if (
            move.active.origin > 15
            or move.passive.origin > 15
            or move.active.origin < 0
            or move.passive.origin < 0
        ):
            print("invalid coordinates")
            return None

        move.passive.destination = self.get_move_destination(
            move.passive.origin, move.direction.cardinal, move.direction.length
        )
        move.active.destination = self.get_move_destination(
            move.active.origin, move.direction.cardinal, move.direction.length
        )

        return move

    def run_command(self, command):
        move_pattern = r"""
            ^                         
            ([a-d])               
            (\d{1,2})               
            (n|nw|w|sw|s|se|e|ne)     
            ([1-2])
            [,\s]+               
            ([a-d])          
            (\d{1,2})          
            .*                
            $                         
        """

        move_regex = re.compile(move_pattern, re.VERBOSE | re.IGNORECASE)

        match = move_regex.match(command)

        if command == "quit" or command == "q" or command == ":q":
            print("exiting...")
            return False
        elif command == "read":
            self.pretty_print()
            return True
        elif command == "restart":
            self.initialize_board()
            return True
        # move syntax match
        elif match:
            move = self.parse_move(match)
            if not move:
                return True
            print(move)

            if not self.is_move_legal(move):
                return False

            return True
        else:
            print("invalid input")
            return True


game = Game()
game.pretty_print

print("Enter 'quit' to exit.")
while True:
    user_input = input("~> ").strip().lower()
    if not game.run_command(user_input):
        break
