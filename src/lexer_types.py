from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class Char:
    char: str
    line: int
    col: int

    @property
    def loc(self) -> str:
        return f"{self.line}:{self.col}"

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    STRING = auto()
    CURLY_OPEN = auto()
    CURLY_CLOSE = auto()
    COLON = auto()
    COMMA = auto()

@dataclass
class Token:
    value: str
    typ: TokenType
    line: int
    col: int

    @property
    def loc(self) -> str:
        return f"{self.line}:{self.col}"