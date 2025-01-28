# test_game.py
import pytest

# Import your classes/functions
from game import (
    Game,
    GameError,
    BoardMove,
    Move,
    Direction,
    board_letter_to_index,
    cardinal_to_index,
    player_number_to_color,
    player_color_to_number,
    Rules,
)


def test_game_initialization():
    game = Game()

    assert len(game.boards) == 4, "Expected 4 boards"
    for board in game.boards:
        assert len(board) == 16, "Each board should have 16 positions"
        assert board.count(1) == 4, "Should have 4 black stones (1) on each board"
        assert board.count(2) == 4, "Should have 4 white stones (2) on each board"
        assert board.count(None) == 8, "Should have 8 empty positions on each board"

    assert game.winner is None, "No winner at the start of the game"


def test_legal_passive_move():
    game = Game()

    passive_board = 0
    active_board = 2

    direction = Direction(cardinal=cardinal_to_index("s"), length=1)

    passive = BoardMove(board=passive_board, origin=0, destination=1)
    active = BoardMove(board=active_board, origin=8, destination=12)

    move = Move(passive=passive, active=active, direction=direction)

    try:
        game.play_move(move)
    except GameError as e:
        pytest.fail(f"Move should be legal, but raised GameError: {e}")

    assert game.boards[0][0] is None, "Origin should be empty after the move"
    assert game.boards[0][1] == 1, "Destination should now have black stone"

    assert game.boards[2][8] is None, "Active origin should be empty after the move"
    assert game.boards[2][12] == 1, "Active destination should have black stone"

    assert game.player_turn == 2, "After black plays, it should be white's turn"


def test_illegal_passive_move_onto_occupied():
    """
    Test an illegal passive move attempt (trying to move where there's already a stone).
    In the initial board setup, a5 is None, but a4 has black's stone.
    We'll try to move from a1 -> a4 in 3 steps (which is not even possible for your game
    since max length is 2, but let's just see an example).
    """
    game = Game()

    # Try to move from a1 to a4 in some direction that doesn't make sense
    # or is blocked. We'll forcibly set up something known to be illegal.

    # We'll pick direction "s" (south) with length=2, for instance,
    # but that would place us at a9 in your coordinate system, not a4.
    # Instead, let's deliberately do something that tries to move to an occupied spot.

    direction = Direction(cardinal=cardinal_to_index("s"), length=1)

    # For the sake of example: a1 -> a5 is out-of-range for length=1,
    # but let's attempt an obviously illegal move: a1 -> a5 with length=2
    # while we know that a5 is outside or might be occupied.

    # Actually, let's just do a smaller example: a1 -> a3 if we pretend it's 2 steps east
    # but that runs into a stone, etc.

    # This is contrived, but the main idea is we want an illegal scenario.
    passive = BoardMove(board=0, origin=0, destination=2)
    active = BoardMove(board=2, origin=8, destination=10)
    move = Move(
        passive=passive, active=active, direction=Direction(cardinal=2, length=2)
    )
    # cardinal=2 is "e", length=2 => a1 -> a3

    # By default, a3 has black's stone in the initial setup, so this is illegal for the passive move.

    with pytest.raises(GameError) as exc_info:
        game.play_move(move)

    # The exception message should mention something about not being able to push or destination occupied
    assert "can't push stones with the passive move" in str(exc_info.value)


def test_active_push_two_stones_illegal():
    """
    Test that pushing two stones is illegal.
    We'll try to create a situation where the active move would push
    two consecutive stones. That should raise a GameError.
    """
    game = Game()

    # We'll manipulate the board so that there's a line of two opponent stones
    # where black tries to push them.

    # For instance, let's say we pick board 'c' (index 2) for black's active move.
    # We'll place black at c5 (index=4), and white at c6 (index=5) and c7 (index=6).
    # Then black tries to move from c5 -> c7, effectively pushing c6 -> c7 (which is occupied).

    # Directly modify the board state for test clarity:
    game.boards[2] = [None] * 16
    game.boards[2][4] = 1  # black
    game.boards[2][5] = 2  # white
    game.boards[2][6] = 2  # white
    # Now an attempt to move black from index=4 to index=6 is a push with length=2
    # and there's already a white stone at index=6, plus one at index=5.

    # Passive move can be on board 'a' with a safe placeholder
    passive = BoardMove(board=0, origin=0, destination=1)  # normal legal passive
    direction = Direction(cardinal=cardinal_to_index("e"), length=2)  # east 2 steps
    active = BoardMove(board=2, origin=4, destination=6)

    move = Move(passive=passive, active=active, direction=direction)

    with pytest.raises(GameError) as exc_info:
        game.play_move(move)

    # The error should be about pushing two stones
    assert "can't push 2 stones in a row" in str(exc_info.value)


def test_game_winner_check():
    """
    Test winning condition: if any board no longer contains the opponent's stone,
    the current player wins. For example, black wins if any entire board has no white stones.
    We'll artificially remove white stones from one board and see if black wins.
    """
    game = Game()
    # We'll remove white from board[0] entirely
    game.boards[0] = [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
    ]  # all black, no white

    # Check if the game sees black as winner:
    game.check_win()
    assert (
        game.winner == 1
    ), "Black should be declared winner because board[0] has no white stones."
