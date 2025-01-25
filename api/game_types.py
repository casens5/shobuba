from typing import List, Optional, Literal

PlayerColorType = Literal["black", "white"]
PlayerNumberType = Literal[1, 2]
MoveLengthType = Literal[1, 2]
CoordinateType = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
BoardNumberType = Literal[0, 1, 2, 3]
BoardLetterType = Literal["a", "b", "c", "d"]
CardinalLetterType = Literal["n", "ne", "e", "se", "s", "sw", "w", "nw"]
CardinalNumberType = Literal[0, 1, 2, 3, 4, 5, 6, 7]
BoardType = List[Optional[PlayerNumberType]]
BoardsType = List[BoardType]
