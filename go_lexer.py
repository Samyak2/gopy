import sys

import colorama
from colorama import Fore, Style

from ply import lex

from symbol_table import SymbolTable

colorama.init()


with open(sys.argv[1], "r") as f:
    input_code = f.read()

if input_code[len(input_code)-1] != '\n':
    input_code += '\n'


insertsemi = False

def set_insertsemi():
    global insertsemi
    if input_code[lexer.lexpos] == '\n':
        insertsemi = True


def find_column(token):
    """Find column number of token"""
    line_start = input_code.rfind("\n", 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


# literal tokens
literals = ';,.=+-*/%()[]{}'


# List of token names.   This is always required
tokens = (
    # assignment operators
    # "EQUALS", # A literal token
    "WALRUS",
    'ADD_EQ',
    'SUB_EQ',
    'MUL_EQ',
    'DIV_EQ',
    'MOD_EQ',
    # TODO : Add |= ^= <<= >>= &= &^=

    # arithmetic operators
    "INCREMENT",
    "DECREMENT", 

    # relational operators
    'EQ_EQ',
    'NOT_EQ',
    'LT',
    'LT_EQ',
    'GT',
    'GT_EQ',

    # literals
    "INT_LIT",
    "FLOAT_LIT",
    "STRING_LIT",
    
    "IDENTIFIER",
    "ELLIPSIS"
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


## tokens to ignore

t_ignore_SPACES = r'\s+'
t_ignore_TABS = r'\t+'
t_ignore_SINGLE_COMMENT =  r'//.*'
t_ignore_MULTI_COMMENT = r'/\*(.|\n)*?\*/'


## tokens with no actions

# assignment operators
# t_EQUALS = r"="
t_WALRUS = r":="
t_ADD_EQ = r'\+='
t_SUB_EQ = r'-='
t_MUL_EQ = r'\*='
t_DIV_EQ = r'/='
t_MOD_EQ = r'%='
# relational operators
t_EQ_EQ = r'=='
t_NOT_EQ = r'!='
t_LT = r'<'
t_LT_EQ = r'<='
t_GT = r'>'
t_GT_EQ = r'>='
# types
t_INT = r"int"
t_FLOAT64 = r"float64"
t_BOOL = r"bool"

t_ELLIPSIS = r"\.\.\."

## tokens with actions


# newline characters
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value) # track line numbers

    global insertsemi
    if insertsemi:
        insertsemi = False
        semi_tok = lex.LexToken()
        semi_tok.type = ';'
        semi_tok.value = ';'
        semi_tok.lineno = t.lexer.lineno
        semi_tok.lexpos = t.lexer.lexpos
        return semi_tok


# closing parantheses

def t_round_end(t):
    r'\)'

    set_insertsemi()
    t.type = ')'
    return t

def t_sq_end(t):
    r'\]'

    set_insertsemi()
    t.type = ']'
    return t

def t_curl_end(t):
    r'\}'

    set_insertsemi()
    t.type = '}'
    return t    


# keywords

def t_BREAK(t):
    r'break'

    set_insertsemi()
    return t

def t_CONTINUE(t):
    r'continue'

    set_insertsemi()
    return t

def t_FALLTHROUGH(t):
    r'fallthrough'

    set_insertsemi()
    return t

def t_RETURN(t):
    r'return'

    set_insertsemi()
    return t


# increment/decrement operators

def t_INCREMENT(t):
    r'\+\+'

    set_insertsemi()
    return t

def t_DECREMENT(t):
    r'--'

    set_insertsemi()
    return t


# literals

def t_STRING_LIT(t):
    r'\"[^\"]*\"'
    
    t.value = ("string", t.value)
    
    set_insertsemi()
    return t


def t_FLOAT_LIT(t):
    r"\d*\.\d+"
    
    t.value = ("float64", float(t.value))
    
    set_insertsemi()
    return t


def t_INT_LIT(t):
    r"\d+"
    
    t.value = ("int", int(t.value))
    
    set_insertsemi()
    return t


# identifier
def t_IDENTIFIER(t):
    r"([a-zA-Z]([a-zA-Z0-9_])*)|_"
    
    if t.value in keywords:
        t.type = keywords[t.value]
    elif t.value in types:
        t.type = types[t.value][0]
    else:
        t.type = "IDENTIFIER"
        symtab.add(t.value)
        t.value = ("identifier", t.value)
    
    set_insertsemi()
    return t


def print_error(err_str):
    print(f"{Fore.RED}ERROR: {err_str}{Style.RESET_ALL}")


# Error handling rule
def t_error(t):
    print_error(f"Illegal character {t.value[0]}")
    col = find_column(t)
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

# Give input to the lexer
lexer.input(input_code)

lines = input_code.split('\n')
symtab = SymbolTable()


if __name__ == "__main__":
    # Tokenize
    for tok in lexer:
        print(tok)
