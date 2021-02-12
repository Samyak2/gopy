import sys

from pptree import print_tree
import colorama
from colorama import Fore, Style

from ply import yacc
import go_lex
from go_lex import tokens, lex, find_column, symtab
from utils import Node


ast = Node("start", node="start")


def p_start(p):
    """start : start expression
    | start top_declaration
    | empty
    """
    ast.add_child(p[1])
    if len(p) > 2:
        ast.add_child(p[2])


def p_expression_addsub(p: yacc.YaccProduction):
    """expression : expression PLUS term
    | expression MINUS term
    | MINUS expression
    | PLUS expression
    """
    if len(p) == 4:
        if p[2] == "+":
            p[0] = Node("+", [p[1], p[3]], p[2])
        elif p[2] == "-":
            p[0] = Node("-", [p[1], p[3]], p[2])
    elif len(p) == 3:
        if p[1] == "+":
            p[0] = Node("+", [p[2]], p[1])
        elif p[1] == "-":
            p[0] = Node("-", [p[2]], p[1])


def p_expression_term(p):
    "expression : term"
    p[0] = p[1]


def p_term_mul_div(p):
    """term : term MULTIPLY factor
    | term DIVIDE factor
    """
    if p[2] == "*":
        p[0] = Node("*", [p[1], p[3]], p[2])
    elif p[2] == "/":
        p[0] = Node("/", [p[1], p[3]], p[2])


def p_term_factor(p):
    "term : factor"
    p[0] = p[1]


def p_factor_num(p):
    """factor : literal
    | IDENTIFIER
    """
    p[0] = p[1]


def p_literal(p):
    """literal : INT_LITERAL
    | FLOAT_LITERAL
    | STRING"""
    p[0] = Node("literal", node=p[1])


def p_factor_expr(p):
    "factor : ROUND_START expression ROUND_END"
    p[0] = p[2]


def p_type(p):
    """type : INT
    | FLOAT64
    | BOOL
    | array_type
    """
    p[0] = p[1]


def p_array_type(p):
    """array_type : SQ_START expression SQ_END type"""
    p[0] = Node("array", node=(p[2], p[4]))


def p_declaration(p):
    """declaration : const_decl
    | var_decl"""
    p[0] = p[1]


def p_top_declaration(p):
    """top_declaration : declaration"""
    p[0] = p[1]


def p_const_decl(p):
    """const_decl : KW_CONST const_spec
    | KW_CONST ROUND_START const_specs ROUND_END
    """
    if len(p) == 3:
        p[0] = Node("const_decl", children=p[2])
    elif len(p) == 5:
        p[0] = Node("const_decl", children=p[3])


def p_const_specs(p):
    """const_specs : const_specs const_spec
    | const_spec
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]


def p_const_spec(p):
    """const_spec : identifier_list EQUAL expression_list
    | identifier_list type EQUAL expression_list
    """
    if len(p) == 4:
        assert len(p[1]) == len(p[3]), "Constant initialisations don't match variables"
        p[0] = [
            Node("identifier", node=(i, None), children=[e]) for i, e in zip(p[1], p[3])
        ]

    elif len(p) == 5:
        assert len(p[1]) == len(p[4]), "Constant initialisations don't match variables"
        p[0] = [
            Node("identifier", node=(i, p[2]), children=[e]) for i, e in zip(p[1], p[4])
        ]


def p_var_decl(p):
    """var_decl : KW_VAR var_spec
    | KW_VAR ROUND_START var_specs ROUND_END
    """
    if len(p) == 3:
        p[0] = Node("var_decl", children=p[2])
    elif len(p) == 5:
        p[0] = Node("var_decl", children=p[3])


def p_var_specs(p):
    """var_specs : var_specs var_spec
    | var_spec
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]


def p_var_spec(p):
    """var_spec : identifier_list EQUAL expression_list
    | identifier_list type EQUAL expression_list
    | identifier_list type
    """
    if len(p) == 3:
        p[0] = [Node("identifier", node=(i, p[2])) for i in p[1]]
    elif len(p) == 4:
        assert len(p[1]) == len(p[3]), "Variable initialisations don't match variables"
        p[0] = [
            Node("identifier", node=(i, None), children=[e]) for i, e in zip(p[1], p[3])
        ]

    elif len(p) == 5:
        assert len(p[1]) == len(p[4]), "Variable initialisations don't match variables"
        p[0] = [
            Node("identifier", node=(i, p[2]), children=[e]) for i, e in zip(p[1], p[4])
        ]


def p_identifier_list(p):
    """identifier_list : IDENTIFIER
    | identifier_list COMMA IDENTIFIER
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]


def p_expression_list(p):
    """expression_list : expression
    | expression_list COMMA expression
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]


def p_empty(p):
    "empty :"
    pass


def p_error(p: lex.LexToken):
    print(f"{Fore.RED}SYNTAX ERROR:{Style.RESET_ALL}")
    if p is not None:
        col = find_column(input_, p)
        print(f"at line {p.lineno}, column {col}")
        print(
            f"{Fore.GREEN}{p.lineno:>10}:\t{Style.RESET_ALL}",
            lines[p.lineno - 1],
            sep="",
        )
        print(" " * 10, " \t", " " * (col - 1), "^", sep="")
    else:
        print("Unexpected end of file")


parser = yacc.yacc(debug=True)


if __name__ == "__main__":
    with open(sys.argv[1], "rt") as f:
        input_ = f.read()
        go_lex.input_ = input_
        lines = input_.split("\n")
        go_lex.lines = lines
        result = parser.parse(input_)
        # print(result)
        print_tree(ast)
        print(symtab)
