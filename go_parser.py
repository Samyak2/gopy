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
        print(str(self))

    def __str__(self):
        return f"<{self.type}, {self.node}>"

    def __repr__(self):
        return f"<Node: {self.type}, {self.node}, {self.children}>"

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
            if not isinstance(child, Node):
                self.children.append(Node(type(child), node=child))
            else:
                self.children.append(child)


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
    """declaration : const_decl"""
    p[0] = p[1]


def p_top_declaration(p):
    """top_declaration : declaration"""
    p[0] = p[1]


def p_const_decl(p):
    """const_decl : CONST const_spec
    | CONST ROUND_START const_specs ROUND_END
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
    print("syntax error go brr!")
    print(f"\tat line {p.lineno}, position {p.lexpos}")


parser = yacc.yacc(debug=True)


if __name__ == "__main__":
    with open(sys.argv[1], "rt") as f:
        result = parser.parse(f.read())
        print(result)
        print_tree(ast)
