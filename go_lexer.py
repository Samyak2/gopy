import sys

import colorama
from colorama import Fore, Style

from ply import lex

from symbol_table import SymbolTable
import utils
from utils import print_line, print_marker, print_lexer_error

colorama.init()


with open(sys.argv[1], "r") as f:
    input_code = f.read()

if input_code[len(input_code) - 1] != "\n":
    input_code += "\n"


# Find column number of token
def find_column(token):
    line_start = input_code.rfind("\n", 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


# Lexing states
states = (("InsertSemi", "exclusive"),)

# List of literal tokens
literals = ";,.=+-*/%()[]{}"

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
    "EXCLAMATION",
    "COLON",
    # assignment operators
    # changes end here
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
    "IDENTIFIER",
    "ELLIPSIS",
)

# List of keywords
keywords = {
    "break"       : "KW_BREAK",
    "default"     : "KW_DEFAULT",
    "func"        : "KW_FUNC",
    "interface"   : "KW_INTERFACE",
    "select"      : "KW_SELECT",
    "case"        : "KW_CASE",
    "defer"       : "KW_DEFER",
    "go"          : "KW_GO",
    "map"         : "KW_MAP",
    "struct"      : "KW_STRUCT",
    "chan"        : "KW_CHAN",
    "else"        : "KW_ELSE",
    "goto"        : "KW_GOTO",
    "package"     : "KW_PACKAGE",
    "switch"      : "KW_SWITCH",
    "const"       : "KW_CONST",
    "fallthrough" : "KW_FALLTHROUGH",
    "if"          : "KW_IF",
    "range"       : "KW_RANGE",
    "type"        : "KW_TYPE",
    "continue"    : "KW_CONTINUE",
    "for"         : "KW_FOR",
    "import"      : "KW_IMPORT",
    "return"      : "KW_RETURN",
    "var"         : "KW_VAR",
}

# List of types
# types -> (symbol, storage in bytes)
types = {
    #For INT
    "int"        : ("INT", 8),
    "int8"       : ("INT8", 1),
    "int16"      : ("INT16", 2),
    "int32"      : ("INT32", 4),
    "int64"      : ("INT64", 8),
    #For Float
    "float32"    : ("FLOAT32", 4),
    "float64"    : ("FLOAT64", 8),
    #For UINT
    "uint"       : ("UINT", 8),
    "uint8"      : ("UINT8", 1),
    "uint16"     : ("UINT16", 2),
    "uint32"     : ("UINT32", 4),
    "uint64"     : ("UINT64", 8),
    #For Complex
    "complex64"  : ("COMPLEX64", 8),
    "complex128" : ("COMPLEX128", 16),
    #For Misc
    "byte"       : ("BYTE", 1),
    "bool"       : ("BOOL", 1),
    "rune"       : ("RUNE", 4)
}

# updating list of tokens with keywords and types
tokens = tokens + tuple(keywords.values()) + tuple(i[0] for i in types.values())


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


t_CARET         = r"\^"
t_RIGHT_SHIFT    = r">>"
t_LEFT_SHIFT     = r"<<"
t_CARET_EQ      = r"\^="
t_BAR_EQ         = r"\|="
t_AMP_EQ         = r"&="
t_AMP_CARET_EQ  = r"&\^="
t_RIGHT_SHIFT_EQ = r">>="
t_LEFT_SHIFT_EQ  = r"<<="
t_AMPERSAND      = r"&"
t_BAR            = r"\|"
t_AMPER_AMPER    = r"&&"
t_BAR_BAR        = r"\|\|"
t_EXCLAMATION    = r"!"
t_COLON          = r":"
t_WALRUS         = r":="
# TODO: Move the assignment operators above, below
# assignment operators
t_ADD_EQ = r'\+='
t_SUB_EQ = r'-='
t_MUL_EQ = r'\*='
t_DIV_EQ = r'/='
t_MOD_EQ = r'%='
# relational operators
t_EQ_EQ  = r"=="
t_NOT_EQ = r"!="
t_LT     = r"<"
t_LT_EQ  = r"<="
t_GT     = r">"
t_GT_EQ  = r">="
# INT type
t_INT   = r"int"
t_INT8  = r"int8"
t_INT16 = r"int16"
t_INT32 = r"int32"
t_INT64 = r"int64"
#FLOAT Type
t_FLOAT32  = r"float32"
t_FLOAT64  = r"float64"
#UNIT Type
t_UINT   = r"uint"
t_UINT8  = r"uint8"
t_UINT16 = r"uint16"
t_UINT32 = r"uint32"
t_UINT64 = r"uint64"
#Complex Type
t_COMPLEX64  = r"complex64"
t_COMPLEX128 = r"complex128"
#MISC Type
t_BOOL = r"bool"
t_RUNE = r"rune"
t_BYTE = r"byte"
t_ELLIPSIS = r"\.\.\."


# tokens with actions


# token in InsertSemi state


def t_InsertSemi_NEWLINE(t):
    r"\n"

    t.lexer.lineno += 1  # track line numbers
    t.lexer.begin("INITIAL")

    semi_tok        = lex.LexToken()
    semi_tok.type   = ";"
    semi_tok.value  = ";"
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


# keywords

def t_KW_BREAK(t):
    r"break"

    t.lexer.begin("InsertSemi")
    return t


def t_KW_CONTINUE(t):
    r"continue"

    t.lexer.begin("InsertSemi")
    return t


def t_KW_FALLTHROUGH(t):
    r"fallthrough"

    t.lexer.begin("InsertSemi")
    return t


def t_KW_RETURN(t):
    r"return"

    t.lexer.begin("InsertSemi")
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
        pos = find_column(t)
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
    r"(true|false|True|False)"

    t.value = ("bool", t.value)

    t.lexer.begin("InsertSemi")
    return t


# identifier
def t_IDENTIFIER(t):
    r"([a-zA-Z]([a-zA-Z0-9_])*)|_"

    # There is no limit on length of identifier in go
    if len(t.value) > 31:
        # TODO print error in a better way
        print_lexer_error("Identifiers must be shorter than 32 characters")
        print_line(t.lexer.lineno)

    if t.value in keywords:
        t.type = keywords[t.value]
    elif t.value in types:
        t.type = types[t.value][0]
    else:
        t.type = "IDENTIFIER"
        t.value = ("identifier", t.value) # why identifier?

    t.lexer.begin('InsertSemi')
    return t


# Error handling rule for ANY state
def t_ANY_error(t):
    print_lexer_error(f"Illegal character {t.value[0]}")
    col = find_column(t)
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
