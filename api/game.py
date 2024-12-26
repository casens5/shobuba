import numpy as np
import re


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
        if self.is_boards_legal(move) and self.is_passive_move_legal(move):
            return True
        else:
            return False

    def is_boards_legal(self, move):
        if (
            move.passive.board == move.active.board
            or (move.passive.board == 0 and move.active.board == 3)
            or (move.passive.board == 1 and move.active.board == 2)
            or (move.passive.board == 2 and move.active.board == 1)
            or (move.passive.board == 3 and move.active.board == 0)
        ):
            print("active and passive moves can't be on the same color")
            return False
        else:
            return True

    def is_passive_move_legal(self, move):
        if (self.playerTurn == "white" and move.passive.board < 2) or (
            self.playerTurn == "black" and move.passive.board > 1
        ):
            print("passive move must be in your home board")
            return False
        else:
            return True

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
        move = {
            "passive": {
                "board": letter_to_index.get(groups[0]),
                "cell": int(groups[1]) - 1,
            },
            "active": {
                "board": letter_to_index.get(groups[4]),
                "cell": int(groups[5]) - 1,
            },
            "direction": {
                "cardinal": cardinal_to_index.get(groups[2]),
                "length": int(groups[3]),
            },
        }

        if (
            move.active.cell > 15
            or move.passive.cell > 15
            or move.active.cell < 0
            or move.passive.cell < 0
        ):
            print("invalid coordinates")
            return None

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
