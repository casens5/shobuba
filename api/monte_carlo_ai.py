class MonteCarloAI:
    def __init__(self):
        pass

    def generate_move(self, boards, player):
        """
        Generate a simple move for the AI.
        In this example, it always moves from A1 to B2.
        """
        from game import Game, Move, BoardMove, Direction

        move = Move(
            passive=BoardMove(board=2, origin=15),  # C,15
            active=BoardMove(board=3, origin=15),  # D,15
            direction=Direction(cardinal=0, length=1),  # Direction: n, length 1
        )
        move.passive.destination = Game.get_move_destination(
            move.passive.origin, move.direction.cardinal, move.direction.length
        )
        move.active.destination = Game.get_move_destination(
            move.active.origin, move.direction.cardinal, move.direction.length
        )
        return move
