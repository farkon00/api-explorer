from lexer import Lexer


def main():
    # TODO: Make filename inputed by argv
    with open("test.ae") as f:
        lexer = Lexer(f.read())
    
    for token in lexer.lex_text():
        print(f"{token.loc} {token.typ} {token.value}")

if __name__ == "__main__":
    main()