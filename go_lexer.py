import sys
import colorama
import utils

from ply import lex
from colorama import Fore, Style
from symbol_table import SymbolTable
from utils import print_line, print_marker, print_lexer_error

colorama.init()

with open(sys.argv[1], "r") as f:
    input_code = f.read()

if input_code[len(input_code) - 1] != "\n":
    input_code += "\n"


# Find column number of token
def find_column(lexpos: int):
    line_start = input_code.rfind("\n", 0, lexpos) + 1
    return (lexpos - line_start) + 1


# Lexing states
states = (("InsertSemi", "exclusive"),)

# List of literal tokens
literals = ";,.=+-*/%()[]!{}"

# List of token names. This is always required
tokens = (
    "CARET",
    "RIGHT_SHIFT",
    "LEFT_SHIFT",
    "CARET_EQ",
    "BAR_EQ",
    "AMP_EQ",
    "AMP_CARET_EQ",
    "RIGHT_SHIFT_EQ",
    "LEFT_SHIFT_EQ",
    "AMPERSAND",
    "BAR",
    "AMPER_AMPER",
    "BAR_BAR",
    #  "EXCLAMATION",
    "COLON",
    # assignment operators
    "WALRUS",
    "ADD_EQ",
    "SUB_EQ",
    "MUL_EQ",
    "DIV_EQ",
    "MOD_EQ",
    # arithmetic operators
    "INCREMENT",
    "DECREMENT",
    # relational operators
    "EQ_EQ",
    "NOT_EQ",
    "LT",
    "LT_EQ",
    "GT",
    "GT_EQ",
    # literals
    "INT_LIT",
    "FLOAT_LIT",
    "STRING_LIT",
    "BOOL_LIT",
    "IDENTIFIER",
    "ELLIPSIS",
)

# List of keywords
keywords = {
    "break": "KW_BREAK",
    "default": "KW_DEFAULT",
    "func": "KW_FUNC",
    "interface": "KW_INTERFACE",
    "select": "KW_SELECT",
    "case": "KW_CASE",
    "defer": "KW_DEFER",
    "go": "KW_GO",
    "map": "KW_MAP",
    "struct": "KW_STRUCT",
    "chan": "KW_CHAN",
    "else": "KW_ELSE",
    "goto": "KW_GOTO",
    "package": "KW_PACKAGE",
    "switch": "KW_SWITCH",
    "const": "KW_CONST",
    "fallthrough": "KW_FALLTHROUGH",
    "if": "KW_IF",
    "range": "KW_RANGE",
    "type": "KW_TYPE",
    "continue": "KW_CONTINUE",
    "for": "KW_FOR",
    "import": "KW_IMPORT",
    "return": "KW_RETURN",
    "var": "KW_VAR",
}

# List of types
# types -> (symbol, storage in bytes)
# types = {}

# updating list of tokens with keywords and types
tokens = tokens + tuple(keywords.values())
unused_tokens = {
    "AMPERSAND",
    "AMP_CARET_EQ",
    "AMP_EQ",
    "BAR",
    "BAR_EQ",
    "CARET",
    "CARET_EQ",
    "COLON",
    "KW_CASE",
    "KW_CHAN",
    "KW_DEFAULT",
    "KW_DEFER",
    "KW_FALLTHROUGH",
    "KW_GO",
    "KW_GOTO",
    "KW_INTERFACE",
    "KW_MAP",
    "KW_SELECT",
    "KW_STRUCT",
    "KW_SWITCH",
    "LEFT_SHIFT",
    "LEFT_SHIFT_EQ",
    "RIGHT_SHIFT",
    "RIGHT_SHIFT_EQ",
}
required_tokens_for_parser = list(set(tokens) - unused_tokens)
#  print(required_tokens_for_parser)

# tokens to ignore in ANY state


def t_ANY_ignore_SPACES(t):
    r"\ +"


def t_ANY_ignore_TABS(t):
    r"\t+"


def t_ANY_ignore_SINGLE_COMMENT(t):
    r"//.*"


def t_ANY_ignore_MULTI_COMMENT(t):
    r"/\*(.|\n)*?\*/"

    t.lexer.lineno += t.value.count("\n")


# tokens with no actions

t_CARET = r"\^"
t_RIGHT_SHIFT = r">>"
t_LEFT_SHIFT = r"<<"
t_CARET_EQ = r"\^="
t_BAR_EQ = r"\|="
t_AMP_EQ = r"&="
t_AMP_CARET_EQ = r"&\^="
t_RIGHT_SHIFT_EQ = r">>="
t_LEFT_SHIFT_EQ = r"<<="
t_AMPERSAND = r"&"
t_BAR = r"\|"
t_AMPER_AMPER = r"&&"
t_BAR_BAR = r"\|\|"
#  t_EXCLAMATION = r"!"
t_COLON = r":"
t_WALRUS = r":="
# TODO: Move the assignment operators above, below
# assignment operators
t_ADD_EQ = r'\+='
t_SUB_EQ = r'-='
t_MUL_EQ = r'\*='
t_DIV_EQ = r'/='
t_MOD_EQ = r'%='
# relational operators
t_EQ_EQ = r"=="
t_NOT_EQ = r"!="
t_LT = r"<"
t_LT_EQ = r"<="
t_GT = r">"
t_GT_EQ = r">="
t_ELLIPSIS = r"\.\.\."

# tokens with actions

# tokens in ANY state


def t_ANY_UNCLOSED_MULTI_COMMENT(t):
    r"/\*(.|\n)*"

    print_lexer_error("Unclosed Multiline comment")
    col = find_column(t.lexpos)
    print(f"at line {t.lineno}, column {col}")
    print(
        f"{Fore.GREEN}{t.lineno:>10}:\t{Style.RESET_ALL}",
        lines[t.lineno - 1],
        sep="",
    )
    print_marker(col - 1, 1)


# token in InsertSemi state


def t_InsertSemi_NEWLINE(t):
    r"\n"

    t.lexer.lineno += 1  # track line numbers
    t.lexer.begin("INITIAL")

    semi_tok = lex.LexToken()
    semi_tok.type = ";"
    semi_tok.value = ";"
    semi_tok.lineno = t.lexer.lineno
    semi_tok.lexpos = t.lexer.lexpos
    return semi_tok


def t_InsertSemi_others(t):
    r"."

    t.lexer.lexpos -= 1
    t.lexer.begin("INITIAL")


# tokens in INITIAL state


# newline characters
def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)  # track line numbers


# closing parantheses


def t_round_end(t):
    r"\)"

    t.lexer.begin("InsertSemi")
    t.type = ")"
    return t


def t_sq_end(t):
    r"\]"

    t.lexer.begin("InsertSemi")
    t.type = "]"
    return t


def t_curl_end(t):
    r"\}"

    t.lexer.begin("InsertSemi")
    t.type = "}"
    return t


# increment/decrement operators


def t_INCREMENT(t):
    r"\+\+"

    t.lexer.begin("InsertSemi")
    return t


def t_DECREMENT(t):
    r"--"

    t.lexer.begin("InsertSemi")
    return t


# literals


def t_STRING_LIT(t):
    r"\"[^\"]*\""

    #  if r"\s*\*/":
    #      print_error("ERROR: Wrong Multiline Comment")
    #      return

    if "\n" in t.value:
        print_lexer_error("string cannot contain line breaks")
        lineno = t.lexer.lineno
        pos = find_column(t.lexpos)
        splits = list(t.value.split("\n"))
        for i, line_ in enumerate(splits):
            print_line(lineno)
            line_actual = lines[lineno - 1]

            if i == 0:
                print_marker(pos - 1, len(line_actual) - pos + 1)
            elif i == len(splits) - 1:
                print_marker(0, line_actual.find('"') + 1)
            else:
                print_marker(0, len(line_actual))

            lineno += 1
        t.lexer.lineno += t.value.count("\n")

        return

    t.value = ("string", t.value)

    t.lexer.begin("InsertSemi")
    return t


def t_FLOAT_LIT(t):
    r"[+-]?(\d+[.]\d*[eE][+-]?\d+)|[+-]?(\d+([.]\d*)|[+-]?\d+([eE][+-]?\d+)|[.]\d+([eE][+-]?\d+)?)"
    t.value = ("float64", float(t.value))

    t.lexer.begin("InsertSemi")
    return t


def t_INT_LIT(t):
    r"\d+"

    t.value = ("int", int(t.value))

    t.lexer.begin("InsertSemi")
    return t


def t_BOOL_LIT(t):
    r"(true|false)"

    t.value = ("bool", t.value)

    t.lexer.begin("InsertSemi")
    return t


# identifier
def t_IDENTIFIER(t):
    r"([a-zA-Z]([a-zA-Z0-9_])*)|_"

    # There is no limit on length of identifier in go
    # if len(t.value) > 31:
    #     # TODO print error in a better way
    #     print_lexer_error("Identifiers must be shorter than 32 characters")
    #     print_line(t.lexer.lineno)

    if t.value in keywords:
        t.type = keywords[t.value]
    else:
        t.type = "IDENTIFIER"
        t.value = ("identifier", t.value, find_column(t.lexpos))

    t.lexer.begin('InsertSemi')
    return t


# Error handling rule for ANY state
def t_ANY_error(t):
    print_lexer_error(f"Illegal character {t.value[0]}")
    col = find_column(t.lexpos)
    print(f"at line {t.lineno}, column {col}")
    print(
        f"{Fore.GREEN}{t.lineno:>10}:\t{Style.RESET_ALL}",
        lines[t.lineno - 1],
        sep="",
    )
    print_marker(col - 1, 1)

    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Give input to the lexer
lexer.input(input_code)

lines = input_code.split("\n")
utils.lines = lines

symtab = SymbolTable()

if __name__ == "__main__":
    # Tokenize
    for tok in lexer:
        print(tok)
