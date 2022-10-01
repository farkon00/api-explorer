from lexer_types import Token, TokenType
from parser_types import *

class Parser:
    TOP_LEVEL_KEYOWRDS = ["def", "route", "response"]
    NESTABLE_KEYWORDS = ["Url", "ArrayOf"] 

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0
        self.defenitions = []

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

    def _parse_response_keyword(self, token: Token) -> Expr:
        route = self._expect_next(TokenType.STRING)
        response = self._expect_next(TokenType.IDENTIFIER)
        if len(response.value) != 3 or not response.value.isnumeric():
            self._error("Responce code must be a 3 digit number")
        form = self._parse_nested_expr()
        if isinstance(form, str):
            self._error("String can't be a format")
        return Expr(ExprType.RESPONSE, [route.value, int(response.value), form], token)

    def _parse_keyword(self, token: Token) -> Expr:
        self._expect(token, TokenType.KEYWORD)
        if token.value == "def":
            name = self._expect_next(TokenType.IDENTIFIER)
            def_value = self._parse_nested_expr()
            if isinstance(def_value, str):
                # TODO: May be it can?
                self._error("String can't be a defenition value")
            self.defenitions.append(name.value)
            return Expr(ExprType.DEF, [name.value, def_value], token)
        elif token.value == "route":
            # TODO: Give a tip if there is code after route 
            route = self._expect_next(TokenType.STRING)
            form = self._parse_nested_expr()
            if isinstance(form, str):
                self._error("String can't be a format")
            return Expr(ExprType.ROUTE, [route.value, form], token)
        elif token.value == "response":
            return self._parse_response_keyword(token)
        elif token.value == "ArrayOf":
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
        return Expr(ExprType.FORMAT, mappings, token)\
        
    def _parse_identifier(self, token: Token) -> Expr:
        if token.value in self.defenitions:
            return Expr(ExprType.LOAD_DEF, [token.value], token)
        else:
            self._error("Unknown name")

    def _parse_nested_expr(self) -> Expr | str:
        token = self._next_token()
        if token.typ == TokenType.KEYWORD:
            if token.value not in self.NESTABLE_KEYWORDS:
                self._error(f"This keyword can't be nested")
            return self._parse_keyword(token)
        elif token.typ == TokenType.STRING:
            return token.value
        elif token.typ == TokenType.IDENTIFIER:
            return self._parse_identifier(token)
        elif token.typ == TokenType.CURLY_OPEN:
            return self._parse_format()
        else:
            self._error("Unexpected token")

    def _parse_top_expr(self) -> Expr:
        """
        Parses one top-level expression
        """
        token = self._expect_next(TokenType.KEYWORD)
        if token.value not in self.TOP_LEVEL_KEYOWRDS:
            self._error("This keyword cannot be used on a top level")
        return self._parse_keyword(token)

    def parse_tokens(self):
        exprs = []
        while self.index < len(self.tokens):
            exprs.append(self._parse_top_expr())
        return exprs