"use client";

import { isEqual } from "lodash-es";
import clsx from "clsx";
import "./board.css";
import Stone from "./stone";
import {
  PlayerColor,
  BoardColor,
  BoardId,
  Length,
  Direction,
  Coord,
  GridType,
  LastMoveType,
  StoneId,
  StoneObject,
  BoardMessage,
  AllowedMove,
  BoardCoordinates,
  NewMove,
} from "./types";
import React, {
  useImperativeHandle,
  forwardRef,
  useState,
  useEffect,
  useRef,
} from "react";

function getMoveLength(
  oldCoords: BoardCoordinates,
  newCoords: BoardCoordinates,
): number {
  return Math.max(
    Math.abs(oldCoords[0] - newCoords[0]),
    Math.abs(oldCoords[1] - newCoords[1]),
  );
}

function getDirection(
  oldCoords: BoardCoordinates,
  newCoords: BoardCoordinates,
): Direction {
  // north/south movement
  if (oldCoords[0] === newCoords[0]) {
    if (oldCoords[1] > newCoords[1]) {
      return Direction.N;
    } else {
      return Direction.S;
    }
  }
  // east/west movement
  if (oldCoords[1] === newCoords[1]) {
    if (oldCoords[0] < newCoords[0]) {
      return Direction.E;
    } else {
      return Direction.W;
    }
  }
  // diagonal
  if (oldCoords[0] < newCoords[0] && oldCoords[1] > newCoords[1]) {
    return Direction.NE;
  } else if (oldCoords[0] < newCoords[0] && oldCoords[1] < newCoords[1]) {
    return Direction.SE;
  } else if (oldCoords[0] > newCoords[0] && oldCoords[1] > newCoords[1]) {
    return Direction.NW;
  } else if (oldCoords[0] > newCoords[0] && oldCoords[1] < newCoords[1]) {
    return Direction.SW;
  }

  console.error("invalid direction: ${oldCoords}, ${newCoords}");
  return Direction.N;
}

// this function is probably too complicated, but makes the transparecy effect
// on LastMove squares not look weird on the corners *shrug emoji*
function getCornerBorder(rowIndex: Coord, colIndex: Coord): string {
  if (rowIndex === 0) {
    if (colIndex === 0) {
      return "rounded-tl-2xl";
    }
    if (colIndex === 3) {
      return "rounded-tr-2xl";
    }
  }
  if (rowIndex === 3) {
    if (colIndex === 0) {
      return "rounded-bl-2xl";
    }
    if (colIndex === 3) {
      return "rounded-br-2xl";
    }
  }
  return "";
}

type CellProps = {
  cell: StoneObject | null;
  row: Coord;
  col: Coord;
  onMouseDownAction: () => void;
  handleMoveStoneAction: (id: StoneId, newPosition: [number, number]) => void;
  className?: string;
};

function Cell({
  cell,
  row,
  col,
  onMouseDownAction,
  handleMoveStoneAction,
  className,
}: CellProps) {
  const cellRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(0);

  useEffect(() => {
    function updateWidth() {
      if (cellRef.current) {
        const width = cellRef.current.getBoundingClientRect().width;
        setContainerWidth(width);
      }
    }

    updateWidth();
    window.addEventListener("resize", updateWidth);

    return () => {
      window.removeEventListener("resize", updateWidth);
    };
  }, []);

  return (
    <div
      key={4 * row + col}
      ref={cellRef}
      onMouseDown={onMouseDownAction}
      className={clsx(
        "box-border aspect-square h-auto w-full touch-none border-black",
        className,
      )}
      style={{
        gridColumn: col + 1,
        gridRow: row + 1,
      }}
    >
      {cell && (
        <Stone
          id={cell.id}
          color={cell.color}
          canMove={cell.canMove}
          containerWidth={containerWidth}
          handleMoveStoneAction={handleMoveStoneAction}
        />
      )}
    </div>
  );
}

type BoardProps = {
  id: BoardId;
  boardColor: BoardColor;
  playerTurn: PlayerColor;
  playerHome: PlayerColor;
  onMove: (newMove: NewMove) => void;
  allowedMove: AllowedMove;
  onMessage: (message: BoardMessage) => void;
};

const Board = forwardRef((props: BoardProps, ref) => {
  const { id, boardColor, playerTurn, onMove, allowedMove, onMessage } = props;

  const [board, setBoard] = useState<GridType>([
    [
      { id: 0, color: "black", canMove: false },
      null,
      null,
      { id: 4, color: "white", canMove: false },
    ],
    [
      { id: 1, color: "black", canMove: false },
      null,
      null,
      { id: 5, color: "white", canMove: false },
    ],
    [
      { id: 2, color: "black", canMove: false },
      null,
      null,
      { id: 6, color: "white", canMove: false },
    ],
    [
      { id: 3, color: "black", canMove: false },
      null,
      null,
      { id: 7, color: "white", canMove: false },
    ],
  ]);

  // change which stones can move based on turn phase
  useEffect(() => {
    // @ts-expect-error typescript is the actual worst
    setBoard((prevBoard) =>
      prevBoard.map((row) =>
        row.map((cell) => {
          if (cell === null) return null;
          return {
            ...cell,
            canMove:
              cell.color === playerTurn &&
              // @ts-expect-error ontuheonuth
              allowedMove.wrongColor == null &&
              // @ts-expect-error ontuheonuth
              allowedMove.notInHomeBoard == null &&
              // @ts-expect-error ontuheonuth
              allowedMove.gameOver == null,
          };
        }),
      ),
    );
  }, [playerTurn, allowedMove]);

  // detect win condition
  useEffect(() => {
    if (
      !board.some((row) => row.some((cell) => cell && cell.color === "black"))
    ) {
      onMessage(BoardMessage.WINWHITE);
    }
    if (
      !board.some((row) => row.some((cell) => cell && cell.color === "white"))
    ) {
      onMessage(BoardMessage.WINBLACK);
    }
  }, [onMessage, board]);

  // record the last player's moves
  const [lastMoveWhite, setLastMoveWhite] = useState<LastMoveType>({
    from: [null, null],
    to: [null, null],
    isPush: false,
  });
  const [lastMoveBlack, setLastMoveBlack] = useState<LastMoveType>({
    from: [null, null],
    to: [null, null],
    isPush: false,
  });

  function getMoveColor(rowIndex: Coord, colIndex: Coord): string {
    if (
      (lastMoveWhite.from[0] === colIndex &&
        lastMoveWhite.from[1] === rowIndex) ||
      (lastMoveBlack.from[0] === colIndex && lastMoveBlack.from[1] === rowIndex)
    ) {
      return "dark-transparent";
    }
    if (
      (lastMoveWhite.isPush &&
        lastMoveWhite.to[0] === colIndex &&
        lastMoveWhite.to[1] === rowIndex) ||
      (lastMoveBlack.isPush &&
        lastMoveBlack.to[0] === colIndex &&
        lastMoveBlack.to[1] === rowIndex)
    ) {
      return "red-transparent";
    }
    if (
      (lastMoveWhite.to[0] === colIndex && lastMoveWhite.to[1] === rowIndex) ||
      (lastMoveBlack.to[0] === colIndex && lastMoveBlack.to[1] === rowIndex)
    ) {
      return "dark-transparent";
    }
    return "";
  }

  // clear the last move via function passed to the parent game
  function clearLastMove(playerColor: PlayerColor) {
    if (playerColor === "white") {
      setLastMoveWhite({
        from: [null, null],
        to: [null, null],
        isPush: false,
      });
    } else {
      setLastMoveBlack({
        from: [null, null],
        to: [null, null],
        isPush: false,
      });
    }
  }

  useImperativeHandle(ref, () => ({
    clearLastMove,
  }));

  // handle board resizing
  const boardRef = useRef<HTMLDivElement>(null);
  const [boardDimensions, setBoardDimensions] = useState({
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
  });

  function updateBoardDimensions() {
    if (boardRef.current) {
      const rect = boardRef.current.getBoundingClientRect();
      setBoardDimensions({
        top: rect.top,
        bottom: rect.bottom,
        left: rect.left,
        right: rect.right,
      });
    }
  }

  useEffect(() => {
    updateBoardDimensions();
    window.addEventListener("resize", updateBoardDimensions);

    return () => {
      window.removeEventListener("resize", updateBoardDimensions);
    };
  }, []);

  function isMoveLegal(
    oldCoords: BoardCoordinates,
    betweenCoords: BoardCoordinates | null,
    newCoords: BoardCoordinates,
    nextCoords: BoardCoordinates | null,
    length: number,
  ): boolean {
    // can't move 3 spaces, or 0 or negative spaces
    if (length < 1 || length > 2) {
      onMessage(BoardMessage.MOVETOOLONG);
      return false;
    }

    // only allow orthogonal or diagonal moves, no knight moves
    const xMove = Math.abs(oldCoords[0] - newCoords[0]);
    const yMove = Math.abs(oldCoords[1] - newCoords[1]);
    if (
      !(xMove === 0 || xMove === length) ||
      !(yMove === 0 || yMove === length)
    ) {
      onMessage(BoardMessage.MOVEKNIGHT);
      return false;
    }

    if (length === 1) {
      // detect push
      if (board[newCoords[0]][newCoords[1]]) {
        // can't push your own stone
        if (board[newCoords[0]][newCoords[1]]!.color === playerTurn) {
          onMessage(BoardMessage.MOVESAMECOLORBLOCKING);
          return false;
        }
        // can't push 2 stones in a row
        if (nextCoords && board[nextCoords[0]][nextCoords[1]]) {
          onMessage(BoardMessage.MOVETWOSTONESBLOCKING);
          return false;
        }
      }
      // unnecessary but legible if (length === 2) and betweenCoords check
    } else if (length === 2 && betweenCoords) {
      // can't push your own stone(s)
      if (
        (board[newCoords[0]][newCoords[1]] &&
          board[newCoords[0]][newCoords[1]]!.color === playerTurn) ||
        (board[betweenCoords[0]][betweenCoords[1]] &&
          board[betweenCoords[0]][betweenCoords[1]]!.color === playerTurn)
      ) {
        onMessage(BoardMessage.MOVESAMECOLORBLOCKING);
        return false;
      }
      // can't push 2 stones in a row
      if (
        Number(board[betweenCoords[0]][betweenCoords[1]] != null) +
          Number(board[newCoords[0]][newCoords[1]] != null) +
          Number(nextCoords && board[nextCoords[0]][nextCoords[1]] != null) >
        1
      ) {
        onMessage(BoardMessage.MOVETWOSTONESBLOCKING);
        return false;
      }
    }

    // move is legal
    return true;
  }

  const handleMoveStoneAction = (
    stoneId: StoneId,
    newPosition: [number, number],
  ) => {
    const newCoords = [
      Math.floor(
        (4 * (newPosition[0] - boardDimensions.left)) /
          (boardDimensions.right - boardDimensions.left),
      ),
      Math.floor(
        (4 * (newPosition[1] - boardDimensions.top)) /
          (boardDimensions.bottom - boardDimensions.top),
      ),
    ] as [Coord, Coord];
    if (
      newCoords[0] > 3 ||
      newCoords[0] < 0 ||
      newCoords[1] > 3 ||
      newCoords[1] < 0
    ) {
      onMessage(BoardMessage.MOVEOUTOFBOUNDS);
      return; // exit; move is out of bounds
    }

    // get previous stone coordinates and color by its id
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    let oldCoords = null;
    let stoneColor = null;
    for (let colIndex = 0; colIndex < board.length; colIndex++) {
      for (let rowIndex = 0; rowIndex < board[colIndex].length; rowIndex++) {
        if (board[colIndex][rowIndex]?.id === stoneId) {
          oldCoords = [colIndex, rowIndex];
          stoneColor = board[colIndex][rowIndex]!.color;
          break;
        }
      }
      if (oldCoords) break;
    }

    if (!oldCoords) {
      console.error("could not get coordinates from stone id");
      return null;
    }
    oldCoords = oldCoords as BoardCoordinates;

    // moved to the starting place.  de-select.
    if (isEqual(oldCoords, newCoords)) {
      onMessage(BoardMessage.MOVECLEARERROR);
      return null;
    }

    const newBoard = [...board];
    let stone = { ...board[oldCoords[0]][oldCoords[1]] };

    // @ts-expect-error onuteh
    if (allowedMove.changePassive != null) {
      oldCoords =
        stoneColor === "white"
          ? (lastMoveWhite.from as BoardCoordinates)
          : (lastMoveBlack.from as BoardCoordinates);

      const deleteCoords =
        stoneColor === "white"
          ? (lastMoveWhite.to as BoardCoordinates)
          : (lastMoveBlack.to as BoardCoordinates);

      stone = { ...board[deleteCoords[0]][deleteCoords[1]] };
      newBoard[deleteCoords[0]][deleteCoords[1]] = null;

      if (isEqual(oldCoords, newCoords)) {
        clearLastMove(stoneColor!);
        // @ts-expect-error ontehuntoeh
        newBoard[newCoords[0]][newCoords[1]] = stone;
        // @ts-expect-error ontehuntoeh
        setBoard(newBoard);
        onMove({ boardId: 0, direction: 0, length: 1, undoPassive: true });
        return;
      }
    }

    const direction = getDirection(oldCoords, newCoords);
    const length = getMoveLength(oldCoords, newCoords) as Length;

    if (
      // @ts-expect-error onuteh
      allowedMove.direction != null &&
      // @ts-expect-error onuteh
      (allowedMove.direction !== direction || allowedMove.length !== length)
    ) {
      onMessage(BoardMessage.MOVEUNEQUALTOPASSIVEMOVE);
      return null;
    }

    const betweenCoords =
      length === 2
        ? ([
            oldCoords[0] + (newCoords[0] - oldCoords[0]) / 2,
            oldCoords[1] + (newCoords[1] - oldCoords[1]) / 2,
          ] as [Coord, Coord])
        : null;
    const nextX = newCoords[0] + (newCoords[0] - oldCoords[0]) / length;
    const nextY = newCoords[1] + (newCoords[1] - oldCoords[1]) / length;
    const nextCoords =
      nextX >= 0 && nextX <= 3 && nextY >= 0 && nextY <= 3
        ? ([nextX, nextY] as [Coord, Coord])
        : null;

    if (!isMoveLegal(oldCoords, betweenCoords, newCoords, nextCoords, length)) {
      return null;
    }

    // check if we're pushing an opponent's stone
    if (
      (length === 1 && board[newCoords[0]][newCoords[1]]) ||
      (length === 2 &&
        (board[betweenCoords![0]][betweenCoords![1]] ||
          board[newCoords[0]][newCoords[1]]))
    ) {
      // can't push if this is the passive move
      // @ts-expect-error onethunoethunth
      if (allowedMove.isPassive != null) {
        onMessage(BoardMessage.MOVEPASSIVECANTPUSH);
        return null;
      }

      const pushedStone =
        length === 1
          ? ({
              ...board[newCoords[0]][newCoords[1]],
            } as StoneObject)
          : ({
              ...(board[betweenCoords![0]][betweenCoords![1]] ||
                board[newCoords[0]][newCoords[1]]),
            } as StoneObject);
      if (nextCoords) {
        newBoard[nextCoords[0]][nextCoords[1]] = pushedStone;
      }

      if (length === 2 && board[betweenCoords![0]][betweenCoords![1]]) {
        newBoard[betweenCoords![0]][betweenCoords![1]] = null;
      }

      if (stoneColor === "white") {
        setLastMoveWhite((prev) => ({
          ...prev,
          isPush: true,
        }));
      } else {
        setLastMoveBlack((prev) => ({
          ...prev,
          isPush: true,
        }));
      }
    }

    // move is successful
    if (stoneColor === "white") {
      setLastMoveWhite((prev) => ({
        ...prev,
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        from: oldCoords,
        to: newCoords,
      }));
    } else {
      setLastMoveBlack((prev) => ({
        ...prev,
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        from: oldCoords,
        to: newCoords,
      }));
    }

    newBoard[oldCoords[0]][oldCoords[1]] = null;
    // @ts-expect-error typescript is bad and ugly
    newBoard[newCoords[0]][newCoords[1]] = stone;
    // @ts-expect-error typescript is bad and ugly
    setBoard(newBoard);

    onMessage(BoardMessage.MOVECLEARERROR);
    onMove({
      boardId: id,
      direction,
      length,
      // @ts-expect-error typescript is bad and ugly
      changePassive: allowedMove.changePassive,
    });
  };

  function showError() {
    // @ts-expect-error onetuhonetuh
    if (allowedMove.notInHomeBoard) {
      onMessage(BoardMessage.MOVENOTINHOMEAREA);
    }
    // @ts-expect-error onetuhonetuh
    if (allowedMove.wrongColor) {
      onMessage(BoardMessage.MOVEWRONGCOLOR);
    }
  }

  return (
    <div
      ref={boardRef}
      className={clsx(
        "grid aspect-square h-auto w-full touch-none grid-cols-4 rounded-2xl",
        {
          "board-dark": boardColor === "dark",
          "board-light": boardColor === "light",
        },
      )}
    >
      {/* @ts-expect-error typescript is bad and ugly */}
      {board.map((col, colIndex: Coord) => {
        // the padding is a weird hack that fixes the spacing for the top
        // right corner of the board
        const rightBorder =
          colIndex !== 3 ? "border-r sm:border-r-2" : "pr-px sm:pr-0.5";

        // @ts-expect-error onetuhnoethunht
        return col.map((cell, rowIndex: Coord) => {
          const bottomBorder = rowIndex !== 3 ? "border-b sm:border-b-2" : "";
          const moveColor = getMoveColor(rowIndex, colIndex);
          const cornerBorder = getCornerBorder(rowIndex, colIndex);

          return (
            <Cell
              key={4 * rowIndex + colIndex}
              row={rowIndex}
              col={colIndex}
              cell={cell}
              handleMoveStoneAction={handleMoveStoneAction}
              className={`${rightBorder} ${bottomBorder} ${cornerBorder} ${moveColor}`}
              onMouseDownAction={showError}
            />
          );
        });
      })}
    </div>
  );
});

Board.displayName = "Board";
export default Board;
