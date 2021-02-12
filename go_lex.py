import sys
from dataclasses import dataclass
from typing import Dict, Tuple

import colorama
from colorama import Fore, Style
from tabulate import tabulate

from ply import lex
from utils import Node

colorama.init()


def find_column(inp_str, token):
    """Find column number of token"""
    line_start = inp_str.rfind("\n", 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


@dataclass
class SymbolInfo:
    """Stores information related to a symbol"""

    depth: int
    lineno: int
    type_: str = None
    storage: int = None
    symbol: Node = None


class SymbolTable:
    """Stores all identifiers, literals and information
    related to them"""

    def __init__(self):
        self.mapping: Dict[Tuple[str, int], SymbolInfo] = {}
        self.depth = 0

    def add(self, symbol: str, lineno: int) -> SymbolInfo:
        if (symbol, self.depth) in self.mapping:
            return self.mapping[symbol, self.depth]

        new_symbol = SymbolInfo(self.depth, lineno)
        self.mapping[symbol, self.depth] = new_symbol

        return new_symbol

    def check_exists(self, symbol) -> bool:
        return (symbol, self.depth) in self.mapping

    def get_if_exists(self, symbol) -> SymbolInfo:
        return self.mapping.get((symbol, self.depth), None)

    def __str__(self):
        return str(
            tabulate(
                [
                    [key[0], key[1], value.type_, value.storage]
                    for key, value in self.mapping.items()
                ],
                headers=["Symbol", "Depth", "Type", "Storage"],
                tablefmt="fancy_grid"
            )
        )


# List of token names.   This is always required
tokens = (
    # operators
    "COMMA",
    "DOT",
    "EQUAL",
    "WALRUS",
    "PLUS",
    "MINUS",
    "MULTIPLY",
    "DIVIDE",
    # literals
    "INT_LITERAL",
    "FLOAT_LITERAL",
    "STRING",
    # parenthesis
    "ROUND_START",
    "ROUND_END",
    "CURL_START",
    "CURL_END",
    "SQ_START",
    "SQ_END",
    "IDENTIFIER",
    "SINGLE_COMMENT",
    "MULTI_COMMENT",
)

keywords = {
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

# types -> (symbol, storage in bytes)
types = {"int": ("INT", 8), "float64": ("FLOAT64", 8), "bool": ("BOOL", 1)}

tokens = tokens + tuple(keywords.values()) + tuple(i[0] for i in types.values())

# Operators
t_COMMA = r","
t_DOT = r"\."
t_EQUAL = r"="
t_WALRUS = r":="
t_PLUS = r"\+"
t_MINUS = r"\-"
t_MULTIPLY = r"\*"
t_DIVIDE = r"/"

# Literals
# t_INT_LITERAL = r"[0-9]+"
# t_FLOAT_LITERAL = r"[0-9]*\.[0-9]+"
t_STRING = r"\"[^\"]*\""


def t_FLOAT_LITERAL(t):
    r"\d*\.\d+"
    t.value = float(t.value)
    return t


def t_INT_LITERAL(t):
    r"\d+"
    t.value = int(t.value)
    return t


# types
t_INT = r"int"
t_FLOAT64 = r"float64"
t_BOOL = r"bool"

# parenthesis
t_ROUND_START = r"\("
t_ROUND_END = r"\)"


def t_CURL_START(t):
    r"\{"
    symtab.depth += 1


def t_CURL_END(t):
    r"\}"
    symtab.depth -= 1


t_SQ_START = r"\["
t_SQ_END = r"\]"


# identifier
def t_IDENTIFIER(t):
    r"([a-zA-Z]([a-zA-Z0-9_])*)|_"
    if t.value in keywords:
        t.type = keywords[t.value]
    elif t.value in types:
        t.type = types[t.value][0]
    else:
        t.type = "IDENTIFIER"
        symtab.add(t.value, t.lineno)

    return t


# comments
def t_SINGLE_COMMENT(t):
    "//.*"


def t_MULTI_COMMENT(t):
    r"/\*(.|\n)*?\*/"


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"


def print_error(err_str):
    print(f"ERROR: {Fore.RED}{err_str}{Style.RESET_ALL}")


# Error handling rule
def t_error(t):
    print_error(f"Illegal character {t.value[0]}")
    col = find_column(input_, t)
    print(f"at line {t.lineno}, column {col}")
    print(
        f"{Fore.GREEN}{t.lineno:>10}:\t{Style.RESET_ALL}",
        lines[t.lineno - 1],
        sep="",
    )
    print(" " * 10, " \t", " " * (col - 1), "^", sep="")

    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
input_ = ""
lines = []
symtab = SymbolTable()


# Give the lexer some input
with open(sys.argv[1], "rt") as f:
    lexer.input(f.read())


if __name__ == "__main__":
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)
