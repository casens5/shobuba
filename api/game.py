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
        groups = [
            letter_to_index.get(groups[0]),
            int(groups[1]) - 1,
            cardinal_to_index.get(groups[2]),
            int(groups[3]),
            letter_to_index.get(groups[4]),
            int(groups[5]) - 1,
        ]

        if (
            groups[1] > 15
            or groups[5] > 15
            or groups[1] < 0
            or groups[5] < 0
            or groups[0] == groups[4]
            or (groups[0] == 0 and groups[4] == 3)
            or (groups[0] == 1 and groups[4] == 2)
            or (groups[0] == 2 and groups[4] == 1)
            or (groups[0] == 3 and groups[4] == 0)
        ):
            print("invalid coordinates")
            return None

        return {
            "passive": [letter_to_index.get(groups[0]), groups[1]],
            "active": [letter_to_index.get(groups[4]), groups[5]],
            "direction": [cardinal_to_index.get(groups[2]), groups[3]],
        }

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
        elif match:
            print(self.parse_move(match))
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
