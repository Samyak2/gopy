from ply import lex

# List of token names.   This is always required
tokens = (
    "COMMA",
    "DOT",
    "EQUAL",
    "WALRUS",
    "INT_LITERAL",
    "FLOAT_LITERAL",
    "INT",
    "FLOAT64",
    "BOOL",
    "PACKAGE",
    "IMPORT",
    "VAR",
    "FUNC",
    "ROUND_START",
    "ROUND_END",
    "CURL_START",
    "CURL_END",
    "STRING",
    "IDENTIFIER"
)

# Operators
t_COMMA = r","
t_DOT = r"."
t_EQUAL = r"="
t_WALRUS = r":="

# Literals
# t_INT_LITERAL = r"[0-9]+"
# t_FLOAT_LITERAL = r"[0-9]*\.[0-9]+"
t_STRING = r"\"[^\"]*\""


def t_INT_LITERAL(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_FLOAT_LITERAL(t):
    r"\d*\.\d+"
    t.value = float(t.value)
    return t


# types
t_INT = r"int"
t_FLOAT64 = r"float64"
t_BOOL = r"bool"

# keywords
t_PACKAGE = r"package"
t_IMPORT = r"import"
t_VAR = r"var"
t_FUNC = r"func"

# parenthesis
t_ROUND_START = r"\("
t_ROUND_END = r"\)"
t_CURL_START = r"\{"
t_CURL_END = r"\}"

# identifier
t_IDENTIFIER = r"[a-zA-Z]([a-zA-Z0-9_])*"


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
with open("test.go", "rt") as f:
    lexer.input(f.read())


# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)

