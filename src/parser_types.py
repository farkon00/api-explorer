from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from lexer_types import Token


class ExprType(Enum):
    DEF = auto()
    ROUTE = auto()
    STATUS = auto()
    LOAD_DEF = auto()
    FORMAT = auto()
    ARRAY_OF = auto()
    URL = auto()

@dataclass
class Expr:
    typ: ExprType
    args: list["Expr" | str] | dict[str, "Expr"]
    token: Token