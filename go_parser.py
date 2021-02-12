import sys

from pptree import print_tree

from ply import yacc
from go_lex import tokens, lex


class Node:
    """Class to store a node of the AST"""

    def __init__(self, type_, children=None, node=None):
        self.type = type_
        if children is not None:
            new_children = []
            for child in children:
                if child is None:
                    continue

                if not isinstance(child, Node):
                    new_children.append(Node(type(child), node=child))
                else:
                    new_children.append(child)
            self.children = new_children
        else:
            self.children = []
        self.node = node

    @staticmethod
    def print_node(child):
        if isinstance(child, Node):
            print(f"{child.type}: {child.node}")
        elif isinstance(child, lex.LexToken):
            print(f"{child.type}: {child.value}")
        else:
            print(f"{child}")

    def print_level_order(self):

        queue = []

        queue.append(self)

        while queue:

            node = queue.pop(0)
            self.print_node(node)

            if isinstance(node, Node):
                queue.extend(node.children)

    def add_child(self, child):
        if child is not None:
            self.children.append(child)


ast = Node("start", node="start")


def p_start(p):
    """start : start expression
    | empty
    """
    ast.add_child(p[1])
    if len(p) > 2:
        ast.add_child(p[2])


def p_expression_addsub(p: yacc.YaccProduction):
    """expression : expression PLUS term
    | expression MINUS term
    """
    if p[2] == "+":
        p[0] = Node("+", [p[1], p[3]], p[2])
    elif p[2] == "-":
        p[0] = Node("-", [p[1], p[3]], p[2])


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
    """factor : number
    | IDENTIFIER
    """
    p[0] = p[1]


def p_number(p):
    """number : INT_LITERAL
    | FLOAT_LITERAL"""
    p[0] = p[1]


def p_factor_expr(p):
    "factor : ROUND_START expression ROUND_END"
    p[0] = p[2]


def p_empty(p):
    "empty :"
    pass


def p_error(p: lex.LexToken):
    print("syntax error go brr!")
    print(f"\tat line {p.lineno}, position {p.lexpos}")


parser = yacc.yacc(debug=True)


if __name__ == "__main__":
    with open(sys.argv[1], "rt") as f:
        result = parser.parse(f.read())
        print(result)
        print_tree(ast, nameattr="node")
