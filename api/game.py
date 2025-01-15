import numpy as np
import re

from dataclasses import dataclass


@dataclass
class BoardMove:
    board: int
    origin: int
    destination: int = None
    is_push: bool = None
    push_destination: int = None


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
    ### initialization and UI functions
    def __init__(self):
        self.boards = []
        self.initialize_boards()
        self.player_turn = "black"
        self.winner = None
        self.letter_to_index = {
            "a": 0,
            "b": 1,
            "c": 2,
            "d": 3,
        }
        self.cardinal_to_index = {
            "n": 0,
            "ne": 1,
            "e": 2,
            "se": 3,
            "s": 4,
            "sw": 5,
            "w": 6,
            "nw": 7,
        }

    def initialize_boards(self):
        self.boards = [
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
        ]

    def print_board(self):
        value_to_symbol = {
            None: ".",
            1: "X",
            2: "O",
        }

        grids = [np.array(row).reshape(4, 4) for row in self.boards]
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

        self.print_current_player()

    def print_current_player(self):
        print(f"{self.player_turn}'s turn")

    ### game logic
    def get_player_number(self):
        return 1 if self.player_turn == "black" else 2

    def change_turn(self):
        if self.player_turn == "black":
            self.player_turn = "white"
        else:
            self.player_turn = "black"

    def check_win(self):
        self.winner = "black" if any(2 not in board for board in self.boards) else None
        self.winner = "white" if any(1 not in board for board in self.boards) else None

    def update_boards(self, move):
        player = self.get_player_number()
        self.boards[move.passive.board][move.passive.origin] = None
        self.boards[move.passive.board][move.passive.destination] = player
        self.boards[move.active.board][move.active.origin] = None
        self.boards[move.active.board][move.active.destination] = player

        if move.active.is_push:
            opponent = 2 if player == 1 else 1
            if move.active.push_destination is not None:
                self.boards[move.active.board][move.active.push_destination] = opponent
            if move.direction.length == 2:
                midpoint = self.get_move_midpoint(
                    move.active.origin, move.active.destination
                )
                self.boards[move.active.board][midpoint] = None

    def get_move_midpoint(self, origin, destination):
        return origin + ((destination - origin) // 2)

    def get_move_destination(self, origin, direction, length):
        x = origin % 4
        y = origin // 4

        # 1 or 2 of these if checks will match
        if direction == 7 or direction < 2:
            y -= length
        if direction > 2 and direction < 6:
            y += length
        if direction > 4:
            x -= length
        if direction > 0 and direction < 4:
            x += length

        if x < 0 or y < 0 or x > 3 or y > 3:
            # out of bounds
            return
        else:
            return (y * 4) + x

    ### move validation
    def is_move_legal(self, move):
        if move.passive.board == move.active.board:
            print("active and passive moves must be on different boards")
            return False

        if (
            (move.passive.board == 0 and move.active.board == 3)
            or (move.passive.board == 1 and move.active.board == 2)
            or (move.passive.board == 2 and move.active.board == 1)
            or (move.passive.board == 3 and move.active.board == 0)
        ):
            print("active and passive moves can't be on the same color")
            return False

        if (self.player_turn == "white" and move.passive.board < 2) or (
            self.player_turn == "black" and move.passive.board > 1
        ):
            print("passive move must be in your home board")
            return False

        player = self.get_player_number()

        if self.boards[move.passive.board][move.passive.origin] is None:
            board_letter = list(self.letter_to_index.keys())[
                list(self.letter_to_index.values()).index(move.passive.board)
            ]
            print(f"no stone exists on {board_letter}{move.passive.origin + 1}")
            return False

        if self.boards[move.passive.board][move.passive.origin] is not player:
            board_letter = list(self.letter_to_index.keys())[
                list(self.letter_to_index.values()).index(move.passive.board)
            ]
            print(
                f"{board_letter}{move.passive.origin + 1} does not belong to {player}"
            )
            return False

        if self.boards[move.active.board][move.active.origin] is None:
            board_letter = list(self.letter_to_index.keys())[
                list(self.letter_to_index.values()).index(move.active.board)
            ]
            print(f"no stone exists on {board_letter}{move.active.origin + 1}")
            return False

        if self.boards[move.active.board][move.active.origin] is not player:
            board_letter = list(self.letter_to_index.keys())[
                list(self.letter_to_index.values()).index(move.active.board)
            ]
            print(f"{board_letter}{move.active.origin + 1} does not belong to {player}")
            return False

        passive_midpoint = (
            self.get_move_midpoint(move.passive.origin, move.passive.destination)
            if move.direction.length == 2
            else None
        )

        if (
            passive_midpoint is not None
            and self.boards[move.passive.board][passive_midpoint] is not None
        ) or self.boards[move.passive.board][move.passive.destination] is not None:
            print("you can't push stones with the passive move")
            return False

        if move.active.is_push:
            stones = bool(self.boards[move.active.board][move.active.destination])

            midpoint = None
            if move.direction.length == 2:
                midpoint = self.get_move_midpoint(
                    move.active.origin, move.active.destination
                )
                stones += bool(self.boards[move.active.board][midpoint])

            if move.active.push_destination is not None:
                stones += bool(
                    self.boards[move.active.board][move.active.push_destination]
                )

            if stones > 1:
                print("you can't push 2 stones in a row")
                return False

            if (
                midpoint is not None
                and self.boards[move.active.board][midpoint] == player
            ) or self.boards[move.active.board][move.active.destination] == player:
                print("you can't push your own color stones")
                return False

        return True

    def is_move_push(self, move):
        move_diff = (
            move.active.destination - move.active.origin
        ) // move.direction.length
        if self.boards[move.active.board][move.active.origin + move_diff] is not None:
            return True
        if (
            move.direction.length == 2
            and self.boards[move.active.board][move.active.origin + (move_diff * 2)]
            is not None
        ):
            return True

        return False

    ### gameplay execution
    def play_move(self, move):
        if self.is_move_push(move):
            move.active.is_push = True
            move.active.push_destination = self.get_move_destination(
                move.active.origin,
                move.direction.cardinal,
                move.direction.length + 1,
            )
        print(move)

        if not self.is_move_legal(move):
            return

        self.update_boards(move)
        self.check_win()
        if self.winner is not None:
            print(f"{self.winner} is the winner")
            return

        self.change_turn()

        self.print_board()

        return

    def parse_move(self, input_match):
        groups = input_match.groups()
        move = Move(
            passive=BoardMove(
                board=self.letter_to_index.get(groups[0]),
                origin=int(groups[1]) - 1,
            ),
            active=BoardMove(
                board=self.letter_to_index.get(groups[4]),
                origin=int(groups[5]) - 1,
            ),
            direction=Direction(
                cardinal=self.cardinal_to_index.get(groups[2]),
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
            return

        move.passive.destination = self.get_move_destination(
            move.passive.origin, move.direction.cardinal, move.direction.length
        )
        move.active.destination = self.get_move_destination(
            move.active.origin, move.direction.cardinal, move.direction.length
        )

        if move.passive.destination is None or move.active.destination is None:
            print("move is out of bounds")
            return

        return move

    def process_user_command(self, command):
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
            return True
        elif command == "read":
            self.print_board()
            return
        elif command == "restart":
            self.initialize_boards()
            self.winner = None
            self.player_turn = "black"
            return
        # move syntax match
        elif match:
            if self.winner is not None:
                print("enter 'restart' to play a new game")
                return

            move = self.parse_move(match)
            if move is None:
                return

            self.play_move(move)

            return
        else:
            print(f"i don't understand input: {command}")
            return


game = Game()
game.print_board()

print("Enter 'quit' to exit.")
while True:
    user_input = input("~> ").strip().lower()
    if game.process_user_command(user_input):
        break
