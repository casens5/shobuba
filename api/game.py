import numpy as np
import re
from dataclasses import dataclass
from typing import List, Optional, Literal, Match

from monte_carlo_ai import MonteCarloAI

PlayerTurnType = Literal["black", "white"]
PlayerNumberType = Literal[1, 2]
MoveLengthType = Literal[1, 2]
CoordinateType = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
BoardNumberType = Literal[0, 1, 2, 3]
BoardLetterType = Literal["a", "b", "c", "d"]
CardinalLetterType = Literal["n", "ne", "e", "se", "s", "sw", "w", "nw"]
CardinalNumberType = Literal[0, 1, 2, 3, 4, 5, 6, 7]
BoardsType = List[List[Optional[PlayerNumberType]]]


LETTER_TO_INDEX = {"a": 0, "b": 1, "c": 2, "d": 3}
INDEX_TO_LETTER = {v: k for k, v in LETTER_TO_INDEX.items()}

CARDINAL_TO_INDEX = {"n": 0, "ne": 1, "e": 2, "se": 3, "s": 4, "sw": 5, "w": 6, "nw": 7}
INDEX_TO_CARDINAL = {v: k for k, v in CARDINAL_TO_INDEX.items()}


def board_letter_to_index(letter: BoardLetterType) -> BoardNumberType:
    return LETTER_TO_INDEX[letter.lower()]  # type: ignore


def index_to_board_letter(index: BoardNumberType) -> BoardLetterType:
    return INDEX_TO_LETTER[index]  # type: ignore


def cardinal_to_index(cardinal: CardinalLetterType) -> CardinalNumberType:
    return CARDINAL_TO_INDEX[cardinal.lower()]  # type: ignore


def index_to_cardinal(index: CardinalNumberType) -> CardinalLetterType:
    return INDEX_TO_CARDINAL[index]  # type: ignore


@dataclass
class BoardMove:
    board: BoardNumberType
    origin: CoordinateType
    destination: CoordinateType
    is_push: Optional[bool] = None
    push_destination: Optional[CoordinateType] = None

    def __repr__(self) -> str:
        return (
            "BoardMove(\n"
            f"  board=            {repr(self.board)},\n"
            f"  origin=           {repr(self.origin)},\n"
            f"  destination=      {repr(self.destination)},\n"
            f"  is_push=          {repr(self.is_push)},\n"
            f"  push_destination= {repr(self.push_destination)},\n"
            ")"
        )

    def __post_init__(self):
        if not (0 <= self.board <= 3):
            raise ValueError(f"board must be between 0 and 3, got {self.board}")

        if not (0 <= self.origin <= 15):
            raise ValueError(f"origin must be between 0 and 15, got {self.origin}")

        if not (0 <= self.destination <= 15):
            raise ValueError(
                f"destination must be between 0 and 15, got {self.destination}"
            )

        if not (0 <= self.push_destination <= 15):
            raise ValueError(
                f"push_destination must be between 0 and 15, got {self.push_destination}"
            )


@dataclass
class Direction:
    cardinal: CardinalNumberType
    length: MoveLengthType

    def __repr__(self) -> str:
        return (
            "Direction(\n"
            f"  cardinal= {repr(self.cardinal)},\n"
            f"  length=   {repr(self.length)},\n"
            ")"
        )

    def __post_init__(self):
        if not (0 <= self.cardinal <= 7):
            raise ValueError(f"cardinal must be between 0 and 7, got {self.cardinal}")

        if not (1 <= self.push_destination <= 2):
            raise ValueError(f"length must be 1 or 2, got {self.length}")


@dataclass
class Move:
    passive: BoardMove
    active: BoardMove
    direction: Direction

    def __repr__(self) -> str:
        return (
            "Move(\n"
            f"  passive=\n{repr(self.passive)},\n"
            f"  active=\n{repr(self.active)},\n"
            f"  direction=\n{repr(self.direction)}\n"
            ")"
        )


class GameError(Exception):
    """baba"""

    pass


class Game:
    ### initialization and UI functions
    def __init__(self) -> None:
        self._boards: BoardsType = []
        self.initialize_boards()
        self._player_turn: PlayerTurnType = "black"
        self._winner: Optional[PlayerTurnType] = None

    @property
    def boards(self) -> BoardsType:
        return self._boards

    @property
    def player_turn(self) -> PlayerTurnType:
        return self._player_turn

    @property
    def winner(self) -> Optional[PlayerTurnType]:
        return self._winner

    def initialize_boards(self) -> None:
        self._boards = [
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
            [1, 1, 1, 1, None, None, None, None, None, None, None, None, 2, 2, 2, 2],
        ]

    @staticmethod
    def print_boards(boards) -> None:
        value_to_symbol = {
            None: ".",
            1: "X",
            2: "O",
        }

        grids = [np.array(row).reshape(4, 4) for row in boards]
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

    def print_current_player(self) -> None:
        print(f"{self._player_turn}'s turn")

    ### game logic
    def get_player_number(self) -> PlayerNumberType:
        return 1 if self._player_turn == "black" else 2

    def change_turn(self) -> None:
        if self._player_turn == "black":
            self._player_turn = "white"
        else:
            self._player_turn = "black"

    def check_win(self) -> None:
        if any(2 not in board for board in self._boards):
            self._winner = "black"
        elif any(1 not in board for board in self._boards):
            self._winner = "white"
        else:
            self._winner = None

    def update_boards(self, move: Move) -> None:
        player = self.get_player_number()
        self._boards[move.passive.board][move.passive.origin] = None
        self._boards[move.passive.board][move.passive.destination] = player
        self._boards[move.active.board][move.active.origin] = None
        self._boards[move.active.board][move.active.destination] = player

        if move.active.is_push:
            opponent = 2 if player == 1 else 1
            if move.active.push_destination is not None:
                self._boards[move.active.board][move.active.push_destination] = opponent  # type: ignore
            if move.direction.length == 2:
                midpoint = Rules.get_move_midpoint(
                    move.active.origin, move.active.destination
                )
                self._boards[move.active.board][midpoint] = None

    ### gameplay execution
    def play_move(self, move: Move) -> None:
        if Rules.is_move_push(move.active, move.direction.length, self._boards):
            move.active.is_push = True
            move.active.push_destination = Rules.get_move_destination(
                move.active.origin,
                move.direction.cardinal,
                move.direction.length + 1,  # type: ignore
            )

        if not Rules.is_move_legal(move, self._boards, self.get_player_number()):
            return

        self.update_boards(move)
        self.check_win()
        if self._winner is not None:
            print(f"{self._winner} is the winner")
            return

        self.change_turn()

        return

    @staticmethod
    # input_match is WhoGivesADamnType
    def parse_move(input_match) -> Move:
        groups = input_match.groups()
        move = Move(
            passive=BoardMove(
                board=board_letter_to_index(groups[0]),
                origin=int(groups[1]) - 1,  # type: ignore
                destination=0,  # placeholder
            ),
            active=BoardMove(
                board=board_letter_to_index(groups[4]),
                origin=int(groups[5]) - 1,  # type: ignore
                destination=0,  # placeholder
            ),
            direction=Direction(
                cardinal=cardinal_to_index(groups[2]),
                length=int(groups[3]),  # type: ignore
            ),
        )

        if move.passive.origin > 15 or move.passive.origin < 0:
            raise GameError(
                f"passive move must be between 1 and 16 (inclusive): recieved move \n{move}"
            )
            return

        if move.active.origin > 15 or move.active.origin < 0:
            raise GameError(
                f"active move must be between 1 and 16 (inclusive): recieved move \n{move}"
            )
            return

        move.passive.destination = Rules.get_move_destination(
            move.passive.origin, move.direction.cardinal, move.direction.length
        )
        move.active.destination = Rules.get_move_destination(
            move.active.origin, move.direction.cardinal, move.direction.length
        )

        if move.passive.destination is None:
            raise GameError(
                f"passive move destination '{move.passive.destination}' is out of bounds.  recieved move \n{move}"
            )
            return

        if move.active.destination is None:
            raise GameError(
                f"active move destination '{move.active.destination}' is out of bounds.  recieved move \n{move}"
            )
            return

        return move

    def process_user_command(self, command: str) -> Literal[True, None]:
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
            self.print_boards(self._boards)
            self.print_current_player()
            return None
        elif command == "restart":
            self.initialize_boards()
            self._winner = None
            self._player_turn = "black"
            return None
        # move syntax match
        elif match:
            if self._winner is not None:
                print("enter 'restart' to play a new game")
                return None

            try:
                move = self.parse_move(match)
            except GameError as e:
                print(e)
                return None

            self.play_move(move)

            self.print_boards(self._boards)
            self.print_current_player()

            return None
        else:
            print(f"i don't understand input: {command}")
            return None


class Rules:
    @staticmethod
    def is_move_legal(move: Move, boards: BoardsType, player: PlayerNumberType) -> bool:
        return Rules.is_passive_legal(
            move.passive, move.direction, boards, player
        ) and Rules.is_active_legal(
            move.active, move.passive, move.direction, boards, player
        )

    @staticmethod
    def is_passive_legal(
        passive_move: BoardMove,
        direction: Direction,
        boards: BoardsType,
        player: PlayerNumberType,
    ) -> bool:
        if (player == 2 and passive_move.board < 2) or (
            player == 1 and passive_move.board > 1
        ):
            print("passive move must be in your home board")
            return False

        if boards[passive_move.board][passive_move.origin] is None:
            board_letter = index_to_board_letter(passive_move.board)
            print(f"no stone exists on {board_letter}{passive_move.origin + 1}")
            return False

        if boards[passive_move.board][passive_move.origin] is not player:
            board_letter = index_to_board_letter(passive_move.board)
            print(
                f"{board_letter}{passive_move.origin + 1} does not belong to {player}"
            )
            return False

        midpoint = (
            Rules.get_move_midpoint(passive_move.origin, passive_move.destination)
            if direction.length == 2
            else None
        )

        if boards[passive_move.board][passive_move.destination] is not None or (
            midpoint is not None and boards[passive_move.board][midpoint] is not None
        ):
            print("you can't push stones with the passive move")
            return False

        return True

    @staticmethod
    def is_active_legal(
        active_move: BoardMove,
        passive_move: BoardMove,
        direction: Direction,
        boards: BoardsType,
        player: PlayerNumberType,
    ) -> bool:
        if passive_move.board == active_move.board:
            print("active and passive moves must be on different boards")
            return False

        if (passive_move.board + active_move.board) == 3:
            """
            same as:
                (passive_move.board == 0 and active_move.board == 3)
                or (passive_move.board == 1 and active_move.board == 2)
                or (passive_move.board == 2 and active_move.board == 1)
                or (passive_move.board == 3 and active_move.board == 0)
            """
            print("active and passive moves can't be on the same color")
            return False

        if boards[active_move.board][active_move.origin] is None:
            board_letter = index_to_board_letter(active_move.board)
            print(f"no stone exists on {board_letter}{active_move.origin + 1}")
            return False

        if boards[active_move.board][active_move.origin] is not player:
            board_letter = index_to_board_letter(active_move.board)
            print(f"{board_letter}{active_move.origin + 1} does not belong to {player}")
            return False

        if active_move.is_push:
            stones = int(bool(boards[active_move.board][active_move.destination]))

            midpoint = None
            if direction.length == 2:
                midpoint = Rules.get_move_midpoint(
                    active_move.origin, active_move.destination
                )
                stones += int(bool(boards[active_move.board][midpoint]))

            if active_move.push_destination is not None:
                stones += int(
                    bool(boards[active_move.board][active_move.push_destination])
                )

            if stones > 1:
                print("you can't push 2 stones in a row")
                return False

            if (
                midpoint is not None and boards[active_move.board][midpoint] == player
            ) or boards[active_move.board][active_move.destination] == player:
                print("you can't push your own color stones")
                return False

        return True

    @staticmethod
    def is_move_push(
        move: BoardMove, length: MoveLengthType, boards: BoardsType
    ) -> bool:
        if length == 2:
            midpoint = Rules.get_move_midpoint(move.origin, move.destination)
            if boards[move.board][midpoint] is not None:
                return True
        if boards[move.board][move.destination] is not None:
            return True

        return False

    @staticmethod
    def get_move_midpoint(
        origin: CoordinateType, destination: CoordinateType
    ) -> CoordinateType:
        return origin + ((destination - origin) // 2)  # type: ignore

    @staticmethod
    def get_move_destination(
        origin: CoordinateType, direction: CoordinateType, length: Literal[1, 2, 3]
    ) -> CoordinateType:
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
            return (y * 4) + x  # type: ignore


if __name__ == "__main__":
    game = Game()
    ai = MonteCarloAI()

    game.print_boards(game.boards)
    game.print_current_player()
    print("enter 'quit' to exit.")

    while True:
        if game.player_turn == "white" and game.winner is None:
            print("AI's turn...")
            move = ai.generate_move(game.boards, "white")
            game.play_move(move)

            game.print_boards(game.boards)
            game.print_current_player()
        else:
            user_input = input("~> ").strip().lower()
            if game.process_user_command(user_input):
                break
