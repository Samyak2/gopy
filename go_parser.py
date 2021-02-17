import sys
import operator

from pptree import print_tree
from colorama import Fore, Style

from ply import yacc

import go_lexer
from go_lexer import tokens, lex, find_column, symtab
from utils import Node


def print_error():
    print(f"{Fore.RED}SYNTAX ERROR:{Style.RESET_ALL}")


def print_line(lineno):
    print(
        f"{Fore.GREEN}{lineno:>10}:\t{Style.RESET_ALL}",
        lines[lineno - 1],
        sep="",
    )


def print_marker(pos, width=1):
    print(
        Fore.YELLOW,
        " " * 10,
        " \t",
        " " * (pos),
        "^" * width,
        Style.RESET_ALL,
        sep="",
    )


# def eval_numeric_op(p1, p2=None, op=None):
#     if op is None:
#         return None
#     if p2 is None:
#         if is_numeric(p1):
#             return Node("numeric", node=(p1.node[0], op(p1.node[1])))
#     if is_numeric(p1) and is_numeric(p2):
#         if p2.node[0] == p2.node[0]:
#             return Node("numeric", node=(p1.node[0], op(p1.node[1], p2.node[1])))
#         else:
#             # TODO: do automatic type casting here
#             raise Exception("aaaaaaaa different types")
#     else:
#         return None


# def is_numeric(p):
#     return isinstance(p, Node) and p.type == "numeric"


# def is_literal(p):
#     return isinstance(p, Node) and p.type == "literal"


# def declare_new_variable(symbol, lineno, type_=None, const=False, value=None):
#     """Helper function to add symbol to the Symbol Table
#     with declaration set to given line number.

#     Prints an error if the symbol is already declared at
#     current depth.
#     """
#     symbol = symbol[1]
#     if symtab.is_declared(symbol):
#         print_error()
#         print(f"Re-declaration of symbol {symbol} at line {lineno}")
#         print_line(lineno)
#         line: str = lines[lineno - 1]
#         # TODO: get correct position of token rather than searching
#         pos = line.find(symbol)
#         width = len(symbol)
#         print_marker(pos, width)
#         other_sym = symtab.get_if_exists(symbol)
#         print(f"{symbol} previously declared at line {other_sym.lineno}")
#         print_line(other_sym.lineno)
#         line: str = lines[other_sym.lineno - 1]
#         pos = line.find(symbol)
#         print_marker(pos, width)
#     else:
#         symtab.update_info(symbol, lineno, type_=type_, const=const, value=value)


# ast = Node("start", node="start")


def p_SourceFile(p):
    '''SourceFile : PackageClause ';' ImportDeclList TopLevelDeclList
    '''

def p_PackageClause(p):
    '''PackageClause : KW_PACKAGE PackageName
    '''

def p_PackageName(p):
    '''PackageName : IDENTIFIER
    '''

def p_ImportDeclList(p):
    '''ImportDeclList : empty
                      | ImportDecl ';' ImportDeclList
    '''

def p_ImportDecl(p):
    '''ImportDecl : KW_IMPORT ImportSpec
                  | KW_IMPORT '(' ImportSpecList ')' 
    '''

def p_ImportSpecList(p):
    '''ImportSpecList : empty
                      | ImportSpec ';' ImportSpecList
    '''

def p_ImportSpec(p):
    '''ImportSpec : empty ImportPath
                  | '.' ImportPath
                  | PackageName ImportPath
    '''

def p_ImportPath(p):
    '''ImportPath : STRING_LIT
    '''

def p_TopLevelDeclList(p):
    '''TopLevelDeclList : empty
                        | TopLevelDecl ';' TopLevelDeclList
    '''

def p_TopLevelDecl(p):
    '''TopLevelDecl : FunctionDecl
                    | Declaration
    '''
    # TODO : Add MethodDecl

def p_FunctionDecl(p):
    '''FunctionDecl : empty
    '''

def p_Declaration(p):
    '''Declaration : VarDecl
    '''

def p_VarDecl(p):
    '''VarDecl : KW_VAR VarSpec
               | KW_VAR '(' VarSpecList ')'
    '''

def p_VarSpecList(p):
    '''VarSpecList : empty
                   | VarSpec ';' VarSpecList
    '''

def p_VarSpec(p):
    '''VarSpec : IdentifierList Type 
               | IdentifierList Type '=' ExpressionList
               | IdentifierList '=' ExpressionList 
    '''

def p_IdentifierList(p):
    '''IdentifierList : IDENTIFIER 
                   | IdentifierList ',' IDENTIFIER
    '''

def p_ExpressionList(p):
    '''ExpressionList : Expression 
                   | ExpressionList ',' Expression
    '''

def p_Expression(p):
    '''Expression : UnaryExpr
                  | Expression BinaryOp Expression
    '''

def p_UnaryExpr(p):
    '''UnaryExpr : IDENTIFIER
                 | UnaryOp UnaryExpr
    '''

def p_UnaryOp(p):
    '''UnaryOp : PLUS 
               | MINUS
    '''
    # TODO : Add other unary operators

def p_BinaryOp(p):
    '''BinaryOp : ArithmeticOp
                | RelationalOp
    '''
    # TODO : Add Logical Operators 
    # TODO : Add other binary operators

def p_ArithmeticOp(p):
    '''ArithmeticOp : PLUS
                    | MINUS
                    | MULTIPLY
                    | DIVIDE
                    | MODULO
    '''


# def p_start(p):
#     """start : start expression
#     | start top_declaration
#     | empty
#     """
#     ast.add_child(p[1])
#     if len(p) > 2:
#         ast.add_child(p[2])


# def p_expression_addsub(p: yacc.YaccProduction):
#     """expression : expression PLUS term
#     | expression MINUS term
#     | MINUS expression
#     | PLUS expression
#     """
#     if len(p) == 4:
#         if p[2] == "+":
#             p[0] = eval_numeric_op(p[1], p[3], operator.add)
#             if p[0] is None:
#                 p[0] = Node("+", [p[1], p[3]], p[2])

#         elif p[2] == "-":
#             p[0] = eval_numeric_op(p[1], p[3], operator.sub)
#             if p[0] is None:
#                 p[0] = Node("-", [p[1], p[3]], p[2])
#     elif len(p) == 3:
#         if p[1] == "+":
#             p[0] = eval_numeric_op(p[2], op=operator.pos)
#             if p[0] is None:
#                 p[0] = Node("+", [p[2]], p[1])
#         elif p[1] == "-":
#             p[0] = eval_numeric_op(p[2], op=operator.neg)
#             if p[0] is None:
#                 p[0] = Node("-", [p[2]], p[1])


# def p_expression_term(p):
#     "expression : term"
#     p[0] = p[1]


# def p_term_mul_div(p):
#     """term : term MULTIPLY factor
#     | term DIVIDE factor
#     """
#     if p[2] == "*":
#         p[0] = eval_numeric_op(p[1], p[3], operator.mul)
#         if p[0] is None:
#             p[0] = Node("*", [p[1], p[3]], p[2])

#     elif p[2] == "/":
#         p[0] = eval_numeric_op(p[1], p[3], operator.truediv)
#         if p[0] is None:
#             p[0] = Node("/", [p[1], p[3]], p[2])


# def p_term_factor(p):
#     "term : factor"
#     p[0] = p[1]


# def p_factor_num(p):
#     """factor : literal
#     | IDENTIFIER
#     """
#     if isinstance(p[1], tuple) and p[1][0] == "identifier":
#         symbol_name = p[1][1]
#         if not symtab.is_declared(p[1][1]):
#             lineno = p.lineno(1)
#             print_error()
#             print(f"{symbol_name} not declared in this scope at line {lineno}")

#             print_line(lineno)
#             line: str = lines[lineno - 1]
#             # TODO: get correct position of token rather than searching
#             pos = line.find(symbol_name)
#             width = len(symbol_name)
#             print_marker(pos, width)
#         else:
#             sym = symtab.get_if_exists(symbol_name)
#             sym.uses.append(p.lineno(1))

#     p[0] = p[1]


# def p_numeric(p):
#     """numeric : INT_LITERAL
#     | FLOAT_LITERAL
#     """
#     p[0] = Node("numeric", node=p[1])


# def p_literal(p):
#     """literal : numeric
#     | STRING"""
#     if isinstance(p[1], Node):
#         p[0] = p[1]
#     else:
#         p[0] = Node("literal", node=p[1])


# def p_factor_expr(p):
#     "factor : ROUND_START expression ROUND_END"
#     p[0] = p[2]


# def p_type(p):
#     """type : INT
#     | FLOAT64
#     | BOOL
#     | array_type
#     """
#     p[0] = p[1]


# def p_array_type(p):
#     """array_type : SQ_START expression SQ_END type"""
#     p[0] = Node("array", node=(p[2], p[4]))


# def p_declaration(p):
#     """declaration : const_decl
#     | var_decl"""
#     p[0] = p[1]


# def p_top_declaration(p):
#     """top_declaration : declaration"""
#     p[0] = p[1]


# def p_const_decl(p):
#     """const_decl : KW_CONST const_spec
#     | KW_CONST ROUND_START const_specs ROUND_END
#     """
#     if len(p) == 3:
#         p[0] = Node("const_decl", children=p[2])
#     elif len(p) == 5:
#         p[0] = Node("const_decl", children=p[3])


# def p_const_specs(p):
#     """const_specs : const_specs const_spec
#     | const_spec
#     """
#     if len(p) == 2:
#         p[0] = p[1]
#     elif len(p) == 3:
#         p[0] = p[1] + p[2]


# def p_const_spec(p):
#     """const_spec : identifier_list EQUAL expression_list
#     | identifier_list type EQUAL expression_list
#     """
#     if len(p) == 4:
#         assert len(p[1]) == len(p[3]), "Constant initialisations don't match variables"
#         p[0] = [
#             Node("identifier", node=(i, None), children=[e]) for i, e in zip(p[1], p[3])
#         ]
#         for ident in p[0]:
#             type_ = None
#             if is_numeric(ident.children[0]) or is_literal(ident.children[0]):
#                 type_ = ident.children[0].node[0]
#             declare_new_variable(
#                 ident.node[0],
#                 p.lineno(2),
#                 const=True,
#                 type_=type_,
#                 value=ident.children[0],
#             )

#     elif len(p) == 5:
#         assert len(p[1]) == len(p[4]), "Constant initialisations don't match variables"
#         p[0] = [
#             Node("identifier", node=(i, p[2]), children=[e]) for i, e in zip(p[1], p[4])
#         ]
#         for ident in p[0]:
#             declare_new_variable(
#                 ident.node[0],
#                 p.lineno(3),
#                 const=True,
#                 type_=ident.node[1],
#                 value=ident.children[0],
#             )


# def p_var_decl(p):
#     """var_decl : KW_VAR var_spec
#     | KW_VAR ROUND_START var_specs ROUND_END
#     """
#     if len(p) == 3:
#         p[0] = Node("var_decl", children=p[2])
#     elif len(p) == 5:
#         p[0] = Node("var_decl", children=p[3])


# def p_var_specs(p):
#     """var_specs : var_specs var_spec
#     | var_spec
#     """
#     if len(p) == 2:
#         p[0] = p[1]
#     elif len(p) == 3:
#         p[0] = p[1] + p[2]


# def p_var_spec(p):
#     """var_spec : identifier_list EQUAL expression_list
#     | identifier_list type EQUAL expression_list
#     | identifier_list type
#     """
#     if len(p) == 3:
#         p[0] = [Node("identifier", node=(i, p[2])) for i in p[1]]
#         for ident in p[0]:
#             declare_new_variable(
#                 ident.node[0], p.lineno(2), const=False, type_=ident.node[1]
#             )

#     elif len(p) == 4:
#         assert len(p[1]) == len(p[3]), "Variable initialisations don't match variables"
#         p[0] = [
#             Node("identifier", node=(i, None), children=[e]) for i, e in zip(p[1], p[3])
#         ]
#         for ident in p[0]:
#             type_ = None
#             if is_numeric(ident.children[0]) or is_literal(ident.children[0]):
#                 type_ = ident.children[0].node[0]
#             declare_new_variable(
#                 ident.node[0],
#                 p.lineno(2),
#                 const=True,
#                 type_=type_,
#                 value=ident.children[0],
#             )

#     elif len(p) == 5:
#         assert len(p[1]) == len(p[4]), "Variable initialisations don't match variables"
#         p[0] = [
#             Node("identifier", node=(i, p[2]), children=[e]) for i, e in zip(p[1], p[4])
#         ]
#         for ident in p[0]:
#             declare_new_variable(
#                 ident.node[0],
#                 p.lineno(3),
#                 const=False,
#                 type_=ident.node[1],
#                 value=ident.children[0],
#             )


# def p_identifier_list(p):
#     """identifier_list : IDENTIFIER
#     | identifier_list COMMA IDENTIFIER
#     """
#     if len(p) == 2:
#         p[0] = [p[1]]
#     elif len(p) == 4:
#         p[0] = p[1] + [p[3]]


# def p_expression_list(p):
#     """expression_list : expression
#     | expression_list COMMA expression
#     """
#     if len(p) == 2:
#         p[0] = [p[1]]
#     elif len(p) == 4:
#         p[0] = p[1] + [p[3]]


def p_empty(p):
    "empty :"
    pass


def p_error(p: lex.LexToken):
    print(f"{Fore.RED}SYNTAX ERROR:{Style.RESET_ALL}")
    if p is not None:
        col = find_column(p)
        print(f"at line {p.lineno}, column {col}")
        print_line(p.lineno)
        # print(" " * 10, " \t", " " * (col - 1), "^", sep="")
        print_marker(col - 1, len(p.value))
    else:
        print("Unexpected end of file")


parser = yacc.yacc(debug=True)


if __name__ == "__main__":
    with open(sys.argv[1], "rt") as f:
        input_ = f.read()
        go_lexer.input_ = input_
        lines = input_.split("\n")
        go_lexer.lines = lines
        result = parser.parse(input_, tracking=True)
        # print(result)
        # print_tree(ast)
        print(symtab)
