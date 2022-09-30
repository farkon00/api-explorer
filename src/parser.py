from lexer_types import Token, TokenType
from parser_types import *

class Parser:
    NESTABLE_KEYWORDS = ["Url", "ArrayOf"] 

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def _curr_token(self) -> Token:
        return self.tokens[self.index - 1]

    def _next_token(self) -> Token:
        self.index += 1
        if self.index - 1 >= len(self.tokens):
            self.index -= 1
            self._error("Unexpected EOF")
        return self._curr_token()

    def _error(self, error: str):
        token = self._curr_token()
        print(f"\033[1;31mError {token.loc}:\033[0m {error}")
        print("    " + token.value)
        exit(1)

    def _get_token_name(self, token: Token) -> str:
        return token.typ.name.lower()

    def _expect(self, token: Token, typ: TokenType, string: str | None = None):
        if token.typ != typ:
            self._error(f"Expected {string if string is not None else typ.name.lower()}, got {self._get_token_name(token)}")

    def _expect_next(self, typ: TokenType, string=None) -> Token:
        self._expect(self._next_token(), typ, string)
        return self._curr_token()

    def _parse_string(self):
        return self._expect_next(TokenType.STRING).value

    def _parse_keyword(self, token: Token) -> Expr:
        self._expect(token, TokenType.KEYWORD)
        if token.value == "ArrayOf":
            return Expr(ExprType.ARRAY_OF, [self._parse_nested_expr()], token)
        elif token.value == "Url":
            return Expr(ExprType.URL, [self._parse_string()], token)
        else:
            assert False, f"Not implemented keyword {token.value}"

    def _parse_format_mapping(self):
        name = self._parse_string()
        self._expect_next(TokenType.COLON)
        value = self._parse_nested_expr()
        return name, value

    def _parse_format(self):
        token = self._curr_token()
        mappings = {} 
        while True:
            mapping = self._parse_format_mapping()
            mappings[mapping[0]] = mapping[1]
            if self._next_token().typ == TokenType.CURLY_CLOSE:
                break
            else:
                self._expect(self._curr_token(), TokenType.COMMA)
        return Expr(ExprType.FORMAT, mappings, token)

    def _parse_nested_expr(self) -> Expr | str:
        token = self._next_token()
        if token.typ == TokenType.KEYWORD:
            if token.value not in self.NESTABLE_KEYWORDS:
                self._error(f"This keyword can't be nested")
            return self._parse_keyword(token)
        elif token.typ == TokenType.STRING:
            return token.value
        elif token.typ == TokenType.CURLY_OPEN:
            return self._parse_format()
