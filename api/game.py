import numpy as np


class Game:
    def __init__(self):
        self.board = []
        self.initialize_board()

    def initialize_board(self):
        self.board = [
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
        ]

    def pretty_print(self):
        grids = [np.array(row).reshape(4, 4) for row in self.board]
        grid_layout = np.array(grids).reshape(2, 2, 4, 4)

        print()
        for row in grid_layout:
            for i in range(4):  # For each line in the 4x4 grid
                print("    ".join(" ".join(map(str, grid[i])) for grid in row))
            print()  # Add spacing between grid rows

    def run_command(command):
        if command == "quit" or command == "q" or command == ":q":
            print("exiting...")
            return False
        elif command == "read":
            self.pretty_print()
        elif command == "restart":
            self.initialize_board()


game = Game()
game.pretty_print

print("Enter 'quit' to exit.")
while True:
    user_input = input("~> ").strip().lower()
    if not game.run_command(user_input):
        break
