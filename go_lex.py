import sys
from ply import lex

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
    "MULTI_COMMENT"
)
keywords = {
    "package": "PACKAGE",
    "import": "IMPORT",
    "var": "VAR",
    "func": "FUNC",
    "if": "IF",
    "else": "ELSE",
    "for": "FOR",
    "const": "CONST"
}
types = {
    "int": "INT",
    "float64": "FLOAT64",
    "bool": "BOOL"
}
tokens = tokens + tuple(keywords.values()) + tuple(types.values())

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
t_CURL_START = r"\{"
t_CURL_END = r"\}"
t_SQ_START = r"\["
t_SQ_END = r"\]"


# identifier
def t_IDENTIFIER(t):
    r"[a-zA-Z]([a-zA-Z0-9_])*"
    if t.value in keywords:
        t.type = keywords[t.value]
    elif t.value in types:
        t.type = types[t.value]
    else:
        t.type = "IDENTIFIER"
    return t


# comments
def t_SINGLE_COMMENT(t):
    "//.*"


def t_MULTI_COMMENT(t):
    r"/\*(.|\n)*?\*/"


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


# Give the lexer some input
with open(sys.argv[1], "rt") as f:
    lexer.input(f.read())


if __name__ == "__main__":
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)

