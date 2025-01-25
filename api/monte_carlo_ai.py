from typing import List
from game_types import BoardsType, BoardType, PlayerNumberType, CoordinateType


class MonteCarloAI:
    def __init__(self):
        pass

    @staticmethod
    def generate_move(boards: BoardsType, player: PlayerNumberType):
        from game import Rules, Move, BoardMove, Direction

        move = Move(
            passive=BoardMove(
                board=2, origin=15, destination=0
            ),  # destination is placeholder
            active=BoardMove(
                board=3, origin=15, destination=0
            ),  # destination is placeholder
            direction=Direction(cardinal=0, length=1),
        )
        move.passive.destination = Rules.get_move_destination(
            move.passive.origin, move.direction.cardinal, move.direction.length
        )
        move.active.destination = Rules.get_move_destination(
            move.active.origin, move.direction.cardinal, move.direction.length
        )
        return move

    @staticmethod
    def get_stones_from_board(
        board: BoardType, player: PlayerNumberType
    ) -> List[CoordinateType]:
        return [index for index, stone in enumerate(board) if stone == player]  # type: ignore
