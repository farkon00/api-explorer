from lexer import Lexer
from parser import Parser
from parser_types import Expr

def expr_to_str(expr):
    res = ""
    if isinstance(expr.args, list):
        for arg in expr.args:
            if isinstance(arg, Expr):
                res += expr_to_str(arg) + "\n"
            else:
                res += str(arg) + "\n"
    else:
        for key, val in expr.args.items():
            res += key + " : " + val + "\n" if isinstance(val, str) else key + " : " + expr_to_str(val)
    return expr.typ.name + "\n  " + "\n  ".join(res.split("\n"))

def main():
    # TODO: Make filename inputed by argv
    with open("foo.ae") as f:
        lexer = Lexer(f.read())
    
    # for token in lexer.lex_text():
    #     print(f"{token.loc} {token.typ} {token.value}")

    parser = Parser(lexer.lex_text())
    exprs = parser.parse_tokens()
    for expr in exprs: 
        print(expr_to_str(expr))

if __name__ == "__main__":
    main()