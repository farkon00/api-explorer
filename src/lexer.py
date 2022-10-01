from typing import Iterator, Optional

from lexer_types import *


class Lexer:
    SPECIAL_CHARS = {
        "{" : TokenType.CURLY_OPEN,
        "}" : TokenType.CURLY_CLOSE,
        ":" : TokenType.COLON,
        "," : TokenType.COMMA
    }

    ESCAPE_CHARACTERS = {
        "\\" : "\\",
        "n" : "\n",
        "t" : "\t",
        "r" : "\r",
        "\"" : "\""
    }
    TOKEN_STOP_CHARS = ["{", "}", ",", ":"]
    KEYWORDS = ["def", "route", "response", "ArrayOf", "Url"]

    def __init__(self, text: str):
        self.text = text 
        self.index = 0
        self.chars = self._characters()

    def _characters(self) -> Iterator[Char]:
        line = 1
        col = 0

        while self.index < len(self.text):
            col += 1
            if self.text[self.index] == "\n":
                line += 1
                col = 1
            yield Char(self.text[self.index], line, col)
            self.index += 1
    
    def _next_char(self):
        try:
            return next(self.chars)
        except StopIteration:
            print("\033[1;31mError:\033[0m Unexpected EOF")

    def _get_string(self):
        is_escaped = False
        string = ""
        while True:
            char = self._next_char()
            if char.char == "\\":
                is_escaped = True
                continue
            if is_escaped:
                if char.char in self.ESCAPE_CHARACTERS:
                    string += self.ESCAPE_CHARACTERS[char.char]
                else:
                    print(f"\033[1;31mError {char.loc}:\033[0m Character \"{char.char}\" isn't coresponding to any escape sequence")
                    exit(1)
                is_escaped = False
            else:
                if char.char == "\"":
                    break
                string += char.char

        return string

    def _lex_alphanum(self, char):
        init_char = char
        token = ""
        eof = False
        while char.char not in self.TOKEN_STOP_CHARS and not char.char.isspace():
            token += char.char
            try:
                char = next(self.chars)
            except StopIteration:
                eof = True
        if not eof and not char.char.isspace():
            self.index -= 1

        if token in self.KEYWORDS:
            return Token(token, TokenType.KEYWORD, init_char.line, init_char.col)
        return Token(token, TokenType.IDENTIFIER, init_char.line, init_char.col)


    def _next_token(self) -> Optional[Token]:
        try:
            char = next(self.chars)
        except StopIteration:
            return

        if char.char.isspace():
            return self._next_token()

        if char.char in self.SPECIAL_CHARS:
            return Token(char.char, self.SPECIAL_CHARS[char.char], char.line, char.col)
        if char.char == "\"":
            return Token(self._get_string(), TokenType.STRING, char.line, char.col)
        else:
            return self._lex_alphanum(char)

    def lex_text(self):
        tokens = []
        while True:
            token = self._next_token()
            if token is None: break
            tokens.append(token)

        return tokens