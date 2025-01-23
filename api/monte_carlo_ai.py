class MonteCarloAI:
    def __init__(self):
        pass

    def generate_move(self, boards, player):
        from game import Rules, Move, BoardMove, Direction

        move = Move(
            passive=BoardMove(board=2, origin=15),
            active=BoardMove(board=3, origin=15),
            direction=Direction(cardinal=0, length=1),
        )
        move.passive.destination = Rules.get_move_destination(
            move.passive.origin, move.direction.cardinal, move.direction.length
        )
        move.active.destination = Rules.get_move_destination(
            move.active.origin, move.direction.cardinal, move.direction.length
        )
        return move
