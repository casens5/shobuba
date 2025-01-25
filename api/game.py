import numpy as np
import re
from dataclasses import dataclass
from typing import Optional, Literal, NamedTuple
from game_types import (
    PlayerColorType,
    PlayerNumberType,
    MoveLengthType,
    CoordinateType,
    BoardNumberType,
    BoardLetterType,
    CardinalLetterType,
    CardinalNumberType,
    BoardsType,
)

from monte_carlo_ai import MonteCarloAI


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


def player_color_to_number(player_color: PlayerColorType) -> PlayerNumberType:
    return 1 if player_color == "black" else 2


def player_number_to_color(player_number: PlayerNumberType) -> PlayerColorType:
    return "black" if player_number == 1 else "white"


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

        ### this is being annoying
        #
        # if not (0 <= self.push_destination <= 15):
        #    raise ValueError(
        #        f"push_destination must be between 0 and 15, got {self.push_destination}"
        #    )


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

        if not (1 <= self.length <= 2):
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


class ValidationResult(NamedTuple):
    is_legal: bool
    message: Optional[str]


class GameError(Exception):
    """baba"""

    pass


class Game:
    ### initialization and UI functions
    def __init__(self) -> None:
        self._boards: BoardsType = []
        self.initialize_boards()
        self._player_turn: PlayerNumberType = 1
        self._winner: Optional[PlayerNumberType] = None

    @property
    def boards(self) -> BoardsType:
        return self._boards

    @property
    def player_turn(self) -> PlayerNumberType:
        return self._player_turn

    @property
    def winner(self) -> Optional[PlayerNumberType]:
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
        print(f"{player_number_to_color(self._player_turn)}'s turn")

    ### game logic
    def change_turn(self) -> None:
        if self._player_turn == 1:
            self._player_turn = 2
        else:
            self._player_turn = 1

    def check_win(self) -> None:
        if Rules.check_win(self._boards, 1):
            self._winner = 1
        elif Rules.check_win(self._boards, 2):
            self._winner = 2
        else:
            pass

    ### gameplay execution
    def play_move(self, move: Move) -> None:
        if Rules.is_move_push(move.active, move.direction.length, self._boards):
            move.active.is_push = True
            move.active.push_destination = Rules.get_move_destination(
                move.active.origin,
                move.direction.cardinal,
                move.direction.length + 1,  # type: ignore
            )

        is_legal, reason = Rules.is_move_legal(move, self._boards, self._player_turn)
        if not is_legal:
            raise GameError(reason)

        self._boards = Rules.update_boards(self._boards, move, self._player_turn)
        self.check_win()
        if self._winner is not None:
            print(f"{player_number_to_color(self._winner)} is the winner")
            return None

        self.change_turn()

        return None

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

        if move.active.origin > 15 or move.active.origin < 0:
            raise GameError(
                f"active move must be between 1 and 16 (inclusive): recieved move \n{move}"
            )

        passive_destination = Rules.get_move_destination(
            move.passive.origin, move.direction.cardinal, move.direction.length
        )
        active_destination = Rules.get_move_destination(
            move.active.origin, move.direction.cardinal, move.direction.length
        )

        if passive_destination is None:
            raise GameError(
                f"passive move destination '{move.passive.destination}' is out of bounds.  recieved move \n{move}"
            )
        else:
            move.passive.destination = passive_destination

        if active_destination is None:
            raise GameError(
                f"active move destination '{move.active.destination}' is out of bounds.  recieved move \n{move}"
            )
        else:
            move.active.destination = active_destination

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
            self._player_turn = 1
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

            try:
                self.play_move(move)
            except GameError as e:
                print(e)
                return None

            self.print_boards(self._boards)
            self.print_current_player()

            return None
        else:
            print(f"i don't understand input: {command}")
            return None


class Rules:
    @staticmethod
    def is_move_legal(
        move: Move, boards: BoardsType, player: PlayerNumberType
    ) -> ValidationResult:
        is_legal, reason = Rules.is_passive_legal(
            move.passive, move.direction, boards, player
        )
        if not is_legal:
            return ValidationResult(is_legal, reason)

        is_legal, reason = Rules.is_active_legal(
            move.active, move.passive, move.direction, boards, player
        )
        return ValidationResult(is_legal, reason)

    @staticmethod
    def is_passive_legal(
        passive_move: BoardMove,
        direction: Direction,
        boards: BoardsType,
        player: PlayerNumberType,
    ) -> ValidationResult:
        if (player == 2 and passive_move.board < 2) or (
            player == 1 and passive_move.board > 1
        ):
            if player == 1:
                home_boards = ["a", "b"]
            else:
                home_boards = ["c", "d"]
            reason = f"the passive (first) move must be in one of your home boards.  player is {player_number_to_color(player)}, home boards are {home_boards}"
            return ValidationResult(False, reason)

        if boards[passive_move.board][passive_move.origin] is None:
            board_letter = index_to_board_letter(passive_move.board)
            reason = f"no stone exists on {board_letter}{passive_move.origin + 1}"
            return ValidationResult(False, reason)

        if boards[passive_move.board][passive_move.origin] is not player:
            board_letter = index_to_board_letter(passive_move.board)
            reason = (
                f"{board_letter}{passive_move.origin + 1} does not belong to {player}"
            )
            return ValidationResult(False, reason)

        midpoint = (
            Rules.get_move_midpoint(passive_move.origin, passive_move.destination)
            if direction.length == 2
            else None
        )

        if boards[passive_move.board][passive_move.destination] is not None or (
            midpoint is not None and boards[passive_move.board][midpoint] is not None
        ):
            reason = "you can't push stones with the passive move"
            return ValidationResult(False, reason)

        return ValidationResult(True, None)

    @staticmethod
    def is_active_legal(
        active_move: BoardMove,
        passive_move: BoardMove,
        direction: Direction,
        boards: BoardsType,
        player: PlayerNumberType,
    ) -> ValidationResult:
        if passive_move.board == active_move.board:
            reason = "active and passive moves must be on different boards"
            return ValidationResult(False, reason)

        if (passive_move.board + active_move.board) == 3:
            """
            same as:
                (passive_move.board == 0 and active_move.board == 3)
                or (passive_move.board == 1 and active_move.board == 2)
                or (passive_move.board == 2 and active_move.board == 1)
                or (passive_move.board == 3 and active_move.board == 0)
            """
            reason = "active and passive moves can't be on the same color"
            return ValidationResult(False, reason)

        if boards[active_move.board][active_move.origin] is None:
            board_letter = index_to_board_letter(active_move.board)
            reason = f"no stone exists on {board_letter}{active_move.origin + 1}"
            return ValidationResult(False, reason)

        if boards[active_move.board][active_move.origin] is not player:
            board_letter = index_to_board_letter(active_move.board)
            reason = (
                f"{board_letter}{active_move.origin + 1} does not belong to {player}"
            )
            return ValidationResult(False, reason)

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
                reason = "you can't push 2 stones in a row"
                return ValidationResult(False, reason)

            if (
                midpoint is not None and boards[active_move.board][midpoint] == player
            ) or boards[active_move.board][active_move.destination] == player:
                reason = "you can't push your own color stones"
                return ValidationResult(False, reason)

        return ValidationResult(True, None)

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
    ) -> Optional[CoordinateType]:
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
            return None
        else:
            return (y * 4) + x  # type: ignore

    @staticmethod
    def update_boards(
        boards: BoardsType, move: Move, player: PlayerNumberType
    ) -> BoardsType:
        boards[move.passive.board][move.passive.origin] = None
        boards[move.passive.board][move.passive.destination] = player
        boards[move.active.board][move.active.origin] = None
        boards[move.active.board][move.active.destination] = player

        if move.active.is_push:
            opponent = Rules.get_opponent_number(player)
            if move.active.push_destination is not None:
                boards[move.active.board][move.active.push_destination] = opponent  # type: ignore
            if move.direction.length == 2:
                midpoint = Rules.get_move_midpoint(
                    move.active.origin, move.active.destination
                )
                boards[move.active.board][midpoint] = None

        return boards

    @staticmethod
    def check_win(boards: BoardsType, player: PlayerNumberType) -> bool:
        opponent = Rules.get_opponent_number(player)
        return any(opponent not in board for board in boards)

    @staticmethod
    def get_opponent_number(player: PlayerNumberType) -> PlayerNumberType:
        return 1 if player == 2 else 2


if __name__ == "__main__":
    game = Game()
    ai = MonteCarloAI()

    game.print_boards(game.boards)
    game.print_current_player()
    print("enter 'quit' to exit.")

    while True:
        # if game.player_turn == 2 and game.winner is None:
        #    print("AI's turn...")
        #    move = ai.generate_move(game.boards, "white")
        #    game.play_move(move)

        #    game.print_boards(game.boards)
        #    game.print_current_player()
        # else:
        user_input = input("~> ").strip().lower()
        if game.process_user_command(user_input):
            break
