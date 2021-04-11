import sys
from typing import Tuple

from pptree_mod import print_tree
from colorama import Fore, Style

from ply import yacc

import go_lexer
from go_lexer import required_tokens_for_parser as tokens, lex, find_column, symtab, type_table
import utils
from utils import print_error, print_line, print_marker
import syntree
from tac import intermediate_codegen
from tree_vis import draw_AST


# def eval_numeric_op(p1, p2=None, op=None):
#     if op is None:
#         return None
#     if p2 is None:
#         if is_numeric(p1):
#             return Node("numeric", node=(p1.node[0], op(p1.node[1])))
#     if is_numeric(p1) and is_numeric(p2):
#         if p2.node[0] == p2.node[0]:
#             return Node("numeric", node=(p1.node[0], op(p1.node[1], p2.node[1])))


ast = syntree.Node("start", children=[])

precedence = (
    # ('left', 'IDENTIFIER'),
    # ('left', 'INT', 'BOOL', 'FLOAT64'),
    # ('left', '(', ')'),
    # ('left', ';'),
    # ("right", "WALRUS"),
    # ("right", "=", "WALRUS", "ADD_EQ", "SUB_EQ", "MUL_EQ", "DIV_EQ", "MOD_EQ"),
    ("right", "="),
    ("left", ","),
    ("left", "EQ_EQ", "NOT_EQ", "LT", "LT_EQ", "GT", "GT_EQ"),
    ("left", "+", "-"),
    ("left", "*", "/", "%"),
    ("right", "UNARY"),
)


def p_SourceFile(p):
    """SourceFile : PackageClause ';' ImportDeclList TopLevelDeclList"""
    ast.data = p[1]
    ast.add_child(p[3])
    ast.add_child(p[4])


def p_PackageClause(p):
    """PackageClause : KW_PACKAGE PackageName"""
    p[0] = p[2][1]


def p_PackageName(p):
    """PackageName : IDENTIFIER"""
    p[0] = p[1]


def p_ImportDeclList(p):
    """ImportDeclList : empty
    | ImportDecl ';' ImportDeclList
    """
    if len(p) == 4:
        if p[3] is not None:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = syntree.List([p[1]])


def p_ImportDecl(p):
    """ImportDecl : KW_IMPORT ImportSpec
    | KW_IMPORT '(' ImportSpecList ')'
    """
    if len(p) == 3:
        p[0] = syntree.List([p[2]])
    elif len(p) == 5:
        p[0] = p[3]


def p_ImportSpecList(p):
    """ImportSpecList : empty
    | ImportSpec ';' ImportSpecList
    """
    if len(p) == 4:
        if p[3] is not None:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = syntree.List([p[1]])


def p_ImportSpec(p):
    """ImportSpec : empty ImportPath
    | '.' ImportPath
    | PackageName ImportPath
    """
    if p[1] is not None:
        p[0] = syntree.Import(p[1], p[2])
    else:
        p[0] = syntree.Import(".", p[2])


def p_ImportPath(p):
    """ImportPath : STRING_LIT"""
    p[0] = p[1]


def p_TopLevelDeclList(p):
    """TopLevelDeclList : empty
    | TopLevelDecl ';' TopLevelDeclList
    """
    if len(p) == 4:
        if p[3] is not None:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = syntree.List([p[1]])


def p_TopLevelDecl(p):
    """TopLevelDecl : FunctionDecl
    | Declaration
    """
    # TODO : Add MethodDecl
    p[0] = p[1]


def p_FunctionDecl(p):
    """FunctionDecl : KW_FUNC FunctionName Signature
    | KW_FUNC FunctionName Signature FunctionBody
    """
    if len(p) == 4:
        p[0] = syntree.Function(p[2], p[3], lineno=p.lineno(2))
    elif len(p) == 5:
        p[0] = syntree.Function(p[2], p[3], body=p[4], lineno=p.lineno(2))
    symtab.leave_scope()


def p_FunctionDecl_error(p):
    """FunctionDecl : KW_FUNC FunctionName error
    | KW_FUNC FunctionName error FunctionBody
    """
    print_error("Error in function declaration")


def p_FunctionName(p):
    """FunctionName : IDENTIFIER"""
    p[0] = p[1]
    symtab.add_if_not_exists(p[1][1])
    syntree.Function.add_func_to_symtab(p[1][1], p.lineno(1))
    symtab.enter_scope()


def p_Signature(p):
    """Signature : Parameters
    | Parameters Result
    """
    if len(p) == 2:
        p[0] = syntree.Signature(p[1])
    else:
        p[0] = syntree.Signature(p[1], p[2])


def p_Parameters(p):
    """Parameters : '(' empty ')'
    | '(' ParameterList ')'
    | '(' ParameterList ',' ')'
    """
    p[0] = p[2]


def p_Result(p):
    """Result : Parameters
    | TypeName
    | TypeLit
    """
    p[0] = p[1]


def p_ParameterList(p):
    """ParameterList : ParameterDecl
    | ParameterList ',' ParameterDecl
    """
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = syntree.List([p[1]])


def p_ParameterDecl(p):
    """ParameterDecl : Type
    | ELLIPSIS Type
    | IdentifierList Type
    | IdentifierList ELLIPSIS Type
    """
    if len(p) == 2:
        p[0] = syntree.ParameterDecl(p[1])
    elif len(p) == 3:
        if isinstance(p[1], syntree.List):
            for ident in p[1]:
                ident.add_symtab()
            p[0] = syntree.ParameterDecl(p[2], ident_list=p[1])
        else:
            p[0] = syntree.ParameterDecl(p[2], vararg=True)
    elif len(p) == 4:
        for ident in p[1]:
            ident.add_symtab()
        p[0] = syntree.ParameterDecl(p[3], vararg=True, ident_list=p[1])


def p_FunctionBody(p):
    """FunctionBody : Block"""
    p[0] = p[1]


def p_Block(p):
    """Block : '{' new_scope StatementList '}' """
    p[0] = p[3]
    symtab.leave_scope()


def p_new_scope(p):
    """new_scope :"""
    symtab.enter_scope()


def p_leave_scope(p):
    """leave_scope :"""
    symtab.leave_scope()


def p_StatementList(p):
    """StatementList : empty
    | Statement ';' StatementList
    """
    if len(p) == 4:
        if p[3] is not None:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = syntree.List([p[1]])


def p_Statement(p):
    """Statement : Block
    | ReturnStmt
    | BreakStmt
    | ContinueStmt
    | IfStmt
    | ForStmt
    | SimpleStmt
    | Declaration
    """
    # TODO : Add more statements like SwitchStmt
    p[0] = p[1]


def p_ReturnStmt(p):
    """ReturnStmt : KW_RETURN
    | KW_RETURN ExpressionList
    """
    if len(p) == 3:
        p[0] = syntree.Keyword("RETURN", children=[p[2]])


def p_BreakStmt(p):
    """BreakStmt : KW_BREAK
    | KW_BREAK Label
    """
    if len(p) == 2:
        p[0] = syntree.Keyword("BREAK")
    elif len(p) == 3:
        p[0] = syntree.Keyword("BREAK", ext=p[2])


def p_Label(p):
    """Label : IDENTIFIER"""
    p[0] = p[1]


def p_ContinueStmt(p):
    """ContinueStmt : KW_CONTINUE
    | KW_CONTINUE Label
    """
    if len(p) == 2:
        p[0] = syntree.Keyword("CONTINUE")
    elif len(p) == 3:
        p[0] = syntree.Keyword("CONTINUE", ext=p[2])


def p_IfStmt(p):
    """IfStmt : KW_IF new_scope Expression Block
    | KW_IF new_scope SimpleStmt ';' Expression Block
    | KW_IF new_scope Expression Block leave_scope KW_ELSE IfStmt
    | KW_IF new_scope Expression Block leave_scope KW_ELSE Block
    | KW_IF new_scope SimpleStmt ';' Expression Block leave_scope KW_ELSE IfStmt
    | KW_IF new_scope SimpleStmt ';' Expression Block leave_scope KW_ELSE Block
    """
    if len(p) == 5:
        p[0] = syntree.IfStmt(body=p[4], expr=p[3])
        symtab.leave_scope()
    elif len(p) == 7:
        p[0] = syntree.IfStmt(body=p[6], expr=p[5], statement=p[3])
        symtab.leave_scope()
    elif len(p) == 8:
        p[0] = syntree.IfStmt(body=p[4], expr=p[3], next_=p[7])
    elif len(p) == 10:
        p[0] = syntree.IfStmt(body=p[6], statement=p[3], expr=p[5], next_=p[9])


def p_ForStmt(p):
    """ForStmt : KW_FOR new_scope Block leave_scope
    | KW_FOR new_scope Condition Block leave_scope
    | KW_FOR new_scope ForClause Block leave_scope
    | KW_FOR new_scope RangeClause Block leave_scope
    """
    if len(p) == 5:
        p[0] = syntree.ForStmt(body=p[3])
    elif len(p) == 6:
        p[0] = syntree.ForStmt(body=p[4], clause=p[3])


def p_Condition(p):
    """Condition : Expression"""
    p[0] = p[1]


def p_ForClause(p):
    """ForClause : InitStmt ';' ';' PostStmt
    | InitStmt ';' Condition ';' PostStmt
    """
    if len(p) == 5:
        p[0] = syntree.ForClause(p[1], cond=None, post=p[4])
    elif len(p) == 6:
        p[0] = syntree.ForClause(p[1], cond=p[3], post=p[5])


def p_InitStmt(p):
    """InitStmt : SimpleStmt"""
    p[0] = p[1]


def p_PostStmt(p):
    """PostStmt : SimpleStmt"""
    p[0] = p[1]


def p_RangeClause(p):
    """RangeClause : KW_RANGE Expression
    | IdentifierList WALRUS KW_RANGE Expression
    | ExpressionList '=' KW_RANGE Expression empty
    """
    if len(p) == 3:
        p[0] = syntree.RangeClause(p[2])
    elif len(p) == 5:
        for ident in p[1]:
            ident.add_symtab()
        p[0] = syntree.RangeClause(p[4], ident_list=p[1])
    elif len(p) == 6:
        p[0] = syntree.RangeClause(p[4], expr_list=p[1])


def p_SimpleStmt(p):
    """SimpleStmt : EmptyStmt
    | ExpressionStmt
    | IncDecStmt
    | Assignment
    | ShortVarDecl
    """
    p[0] = p[1]


def p_EmptyStmt(p):
    """EmptyStmt : empty"""


def p_ExpressionStmt(p):
    """ExpressionStmt : Expression"""
    p[0] = p[1]


def p_IncDecStmt(p):
    """IncDecStmt : Expression INCREMENT
    | Expression DECREMENT
    """
    p[0] = syntree.UnaryOp(p[2], p[1])


def p_Assignment(p):
    """Assignment : ExpressionList assign_op ExpressionList"""
    p[0] = syntree.Assignment(p[2], p[1], p[3])


def p_assign_op(p):
    """assign_op : '='
    | ADD_EQ
    | SUB_EQ
    | MUL_EQ
    | DIV_EQ
    | MOD_EQ
    """
    #     # TODO : Add |= ^= <<= >>= &= &^=
    p[0] = p[1]


def p_ShortVarDecl(p):
    """ShortVarDecl : IdentifierList WALRUS ExpressionList"""
    ident_list = p[1]
    for ident in ident_list:
        ident.add_symtab()
    expr_list = p[3]
    p[0] = syntree.make_variable_decls(ident_list, expression_list=expr_list)


def p_Declaration(p):
    """Declaration : VarDecl
    | ConstDecl
    | TypeDecl
    """
    p[0] = p[1]


def p_VarDecl(p):
    """VarDecl : KW_VAR VarSpec
    | KW_VAR '(' VarSpecList ')'
    """
    if len(p) == 3:
        p[0] = syntree.List([p[2]])
    elif len(p) == 5:
        p[0] = p[3]


def p_VarSpecList(p):
    """VarSpecList : empty
    | VarSpec ';' VarSpecList
    """
    if len(p) == 4:
        if p[3] is not None:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = syntree.List([p[1]])


def p_VarSpec(p):
    """VarSpec : IdentifierList Type
    | IdentifierList Type '=' ExpressionList
    | IdentifierList '=' ExpressionList
    """
    for ident in p[1]:
        ident.add_symtab()

    if len(p) == 3:
        p[0] = syntree.make_variable_decls(p[1], p[2])
    elif len(p) == 4:
        p[0] = syntree.make_variable_decls(p[1], expression_list=p[3])
    elif len(p) == 5:
        p[0] = syntree.make_variable_decls(p[1], p[2], p[4])


def p_ConstDecl(p):
    """ConstDecl : KW_CONST ConstSpec
    | KW_CONST '(' ConstSpecList ')'
    """
    if len(p) == 3:
        p[0] = syntree.List([p[2]])
    elif len(p) == 5:
        p[0] = p[3]


def p_ConstSpecList(p):
    """ConstSpecList : empty
    | ConstSpec ';' ConstSpecList
    """
    if len(p) == 4:
        if p[3] is not None:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = syntree.List([p[1]])


def p_ConstSpec(p):
    """ConstSpec : IdentifierList
    | IdentifierList '=' ExpressionList
    | IdentifierList Type '=' ExpressionList
    """
    for ident in p[1]:
        ident.add_symtab()

    if len(p) == 2:
        p[0] = syntree.make_variable_decls(p[1], const=True)
    elif len(p) == 4:
        p[0] = syntree.make_variable_decls(p[1], expression_list=p[3], const=True)
    elif len(p) == 5:
        p[0] = syntree.make_variable_decls(p[1], p[2], p[4], const=True)


def p_TypeDecl(p):
    """TypeDecl : KW_TYPE TypeSpec
    | KW_TYPE '(' TypeSpecList ')'
    """
    if len(p) == 3:
        p[0] = syntree.List([p[2]])
    elif len(p) == 5:
        p[0] = p[3]


def p_TypeSpecList(p):
    """TypeSpecList : empty
    | TypeSpec ';' TypeSpecList
    """
    if len(p) == 4:
        if p[3] is not None:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = syntree.List([p[1]])


def p_TypeSpec(p):
    """TypeSpec : TypeDef
    | AliasDecl
    """
    p[0] = p[1]


def p_TypeDef(p):
    """TypeDef : IDENTIFIER Type"""
    p[0] = syntree.TypeDef(p[1], p[2], type_table, p.lineno(1))


def p_AliasDecl(p):
    """AliasDecl : IDENTIFIER '=' Type"""
    p[0] = syntree.TypeDef(p[1], p[3], type_table, p.lineno(1))


def p_IdentifierList(p):
    """IdentifierList : IDENTIFIER
    | IDENTIFIER ',' IdentifierList
    """
    if len(p) == 2:
        p[0] = syntree.List([syntree.Identifier(p[1], p.lineno(1))])
    elif len(p) == 4:
        p[3].append(syntree.Identifier(p[1], p.lineno(1)))
        p[0] = p[3]


def p_ExpressionList(p):
    """ExpressionList : Expression
    | Expression ',' ExpressionList
    """
    if len(p) == 4:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 2:
        p[0] = syntree.List([p[1]])


def p_Expression(p):
    """Expression : UnaryExpr
    | Expression '+' Expression
    | Expression '-' Expression
    | Expression '*' Expression
    | Expression '/' Expression
    | Expression '%' Expression
    | Expression EQ_EQ Expression
    | Expression NOT_EQ Expression
    | Expression LT Expression
    | Expression LT_EQ Expression
    | Expression GT Expression
    | Expression GT_EQ Expression
    """
    # TODO : Add Logical Operators
    # TODO : Add other binary operators

    if len(p) == 4:
        p[0] = syntree.BinOp(p[2], left=p[1], right=p[3])
    else:
        p[0] = p[1]


def p_UnaryExpr(p):
    """UnaryExpr : PrimaryExpr
    | UnaryOp UnaryExpr
    """
    if len(p) == 3:
        p[0] = syntree.UnaryOp(p[1], p[2])
    else:
        # TODO : handle more stuff in PrimaryExpr
        # also change the PrimaryExpr class in syntree when doing so
        # p[0] = syntree.UnaryOp(None, p[1])
        p[0] = p[1]


def p_UnaryOp(p):
    """UnaryOp : '+' %prec UNARY
    | '-' %prec UNARY
    """
    # TODO : Add other unary operators
    p[0] = p[1]


def p_PrimaryExpr(p):
    """PrimaryExpr : Operand
    | PrimaryExpr Arguments
    | PrimaryExpr Index
    """
    # TODO : This is too less! Many more to add
    if len(p) == 2:
        if isinstance(p[1], syntree.Node):
            # p[0] = syntree.PrimaryExpr(operand=None, children=[p[1]])
            p[0] = p[1]
        else:
            p[0] = syntree.PrimaryExpr(operand=p[1])
    elif len(p) == 3:
        p[0] = syntree.PrimaryExpr(operand=None, children=[p[1], p[2]])


def p_Arguments(p):
    """Arguments : '(' ')'
    | '(' ExpressionList ')'
    """
    if len(p) == 3:
        p[0] = syntree.Arguments(None)
    elif len(p) == 4:
        p[0] = syntree.Arguments(p[2])


def p_Index(p):
    """Index : '[' Expression ']'
    """
    p[0] = syntree.Index(p[2])


def p_Operand(p):
    """Operand : OperandName
    | Literal
    | '(' Expression ')'
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2]


def p_OperandName(p):
    """OperandName : IDENTIFIER %prec '='
    | QualifiedIdent
    """
    if not isinstance(p[1], syntree.QualifiedIdent):
        ident: Tuple = p[1]
        sym = symtab.get_symbol(ident[1])
        lineno = p.lineno(1)
        if not symtab.is_declared(ident[1]):
            print_error()
            print(f"Undeclared symbol '{ident[1]}' at line {lineno}")
            print_line(lineno)
            line: str = utils.lines[lineno - 1]
            # TODO: get correct position of token rather than searching
            pos = line.find(ident[1])
            width = len(ident[1])
            print_marker(pos, width)
        else:
            sym.uses.append(lineno)

    p[0] = p[1]


def p_QualifiedIdent(p):
    """QualifiedIdent : PackageName '.' IDENTIFIER"""
    p[0] = syntree.QualifiedIdent(p[1], p[3])


def p_Literal(p):
    """Literal : BasicLit
    | FunctionLit
    | CompositeLit"""
    # TODO : Add FunctionLit
    p[0] = p[1]


def p_CompositeLit(p):
    """CompositeLit : LiteralType LiteralValue
    """
    p[0] = syntree.Literal(type_=p[1], value=p[2])


def p_LiteralType(p):
    """LiteralType : ArrayType
    | '[' '.' '.' '.' ']' ElementType
    | TypeName
    | SliceType
    """
    # TODO: add MapType here
    # TODO: add StructType
    if len(p) == 2:
        p[0] = p[1]
    else:
        raise NotImplementedError("Array [...] literal not supported yet")


def p_LiteralValue(p):
    """LiteralValue : '{' ElementList '}'
    """
    if len(p) == 3:
        p[0] = None
    elif len(p) == 4:
        p[0] = p[2]
    elif len(p) == 5:
        p[0] = p[2]
    else:
        raise Exception("Bad grammar or rules!")


def p_ElementList(p):
    """ElementList : KeyedElementList
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        # p[0] = syntree.List([p[1], *p[2]])
        raise Exception("Invalid semantic rules here!")


def p_KeyedElementList(p):
    """KeyedElementList : KeyedElement
    | KeyedElement ',' KeyedElementList
    """
    if len(p) == 2:
        p[0] = syntree.List([p[1]])
    elif len(p) == 4:
        p[3].append(p[1])
        p[0] = p[3]
    else:
        raise Exception("Bad grammar or rules!")


def p_KeyedElement(p):
    """KeyedElement : Element
    """
    # TODO: add `Key ':' Element`
    if len(p) == 2:
        p[0] = (None, p[1])
    elif len(p) == 4:
        p[0] = (p[1], p[3])
    else:
        raise Exception("Bad grammar or rules!")


# def p_Key(p):
#     """Key : FieldName
#     | Expression
#     | LiteralValue
#     """
#     p[0] = p[1]


# def p_FieldName(p):
#     """FieldName : IDENTIFIER
#     """
#     p[0] = p[1]


def p_Element(p):
    """Element : Expression
    | LiteralValue
    """
    p[0] = p[1]


def p_BasicLit(p):
    """BasicLit : int_lit
    | float_lit
    | string_lit
    | bool_lit
    """
    # TODO : Add other basic literals
    p[0] = syntree.Literal(p[1][0], p[1][1])


def p_FunctionLit(p):
    """FunctionLit : KW_FUNC Signature FunctionBody"""
    p[0] = syntree.Function(None, p[2], p[3])


def p_int_lit(p):
    """int_lit : INT_LIT"""

    # TODO :
    # '''int_lit : decimal_lit
    #            | binary_lit
    #            | octal_lit
    #            | hex_lit
    # '''
    p[0] = p[1]


def p_float_lit(p):
    """float_lit : FLOAT_LIT"""

    # TODO :
    # '''float_lit : decimal_float_lit
    #              | hex_float_lit
    # '''
    p[0] = p[1]


def p_string_lit(p):
    """string_lit : STRING_LIT"""

    # TODO :
    # '''string_lit : raw_string_lit
    #               | interpreted_string_lit
    # '''
    p[0] = p[1]


def p_bool_lit(p):
    """bool_lit : BOOL_LIT"""
    p[0] = p[1]


def p_Type(p):
    """Type : TypeName
    | TypeLit
    | '(' Type ')'
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2]


def p_TypeName(p):
    """TypeName : BasicType
    """
    # TODO: QualifiedIdent here gives R/R conflict
    if isinstance(p[1], tuple) and p[1][0] == "identifier":
        p[0] = p[1][1]
    else:
        p[0] = p[1]


def p_BasicType(p):
    """BasicType : INT
    | INT8
    | INT16
    | INT32
    | INT64
    | FLOAT32
    | FLOAT64
    | UINT
    | UINT8
    | UINT16
    | UINT32
    | UINT64
    | COMPLEX64
    | COMPLEX128
    | STRING
    | BYTE
    | BOOL
    | RUNE
    """
    p[0] = syntree.Type(name="BasicType", children=[], data=p[1])


def p_TypeLit(p):
    """TypeLit : ArrayType
    | PointerType
    | FunctionType
    | SliceType
    """
    # TODO : Add other type literals
    # TODO : add StructType
    p[0] = p[1]


def p_ArrayType(p):
    """ArrayType : '[' ArrayLength ']' ElementType"""
    p[0] = syntree.Array(p[4], p[2])


def p_ArrayLength(p):
    """ArrayLength : Expression"""
    p[0] = p[1]


def p_ElementType(p):
    """ElementType : Type"""
    p[0] = p[1]


def p_SliceType(p):
    """SliceType : '[' ']' ElementType
    """
    p[0] = syntree.Slice(p[3])


# def p_StructType(p):
#     """StructType : KW_STRUCT '{' FieldDeclList '}' """
#     p[0] = syntree.Struct(p[3])


# def p_FieldDeclList(p):
#     """FieldDeclList : empty
#     | FieldDeclList FieldDecl ';'
#     """
#     if len(p) == 2:
#         p[0] = syntree.List([])
#     elif len(p) == 4:
#         p[1].append(p[2])
#         p[0] = p[1]
#     else:
#         raise Exception("Invalid grammar?")


# def p_FieldDecl(p):
#     """FieldDecl : IdentifierList Type Tag
#     | EmbeddedField Tag
#     """
#     if len(p) == 4:
#         p[0] = syntree.StructFieldDecl(p[1], p[2], p[3])
#     else:
#         p[0] = syntree.StructFieldDecl(p[1], tag=p[2])


# def p_EmbeddedField(p):
#     """EmbeddedField : '*' TypeName
#     | TypeName"""
#     if p[1] == "*":
#         p[0] = (p[1], p[2])
#     else:
#         p[0] = (None, p[1])


# def p_Tag(p):
#     """Tag : empty
#     | STRING_LIT
#     """
#     p[0] = p[1]


def p_PointerType(p):
    """PointerType : '*' BaseType"""


def p_BaseType(p):
    """BaseType : Type"""
    p[0] = p[1]


def p_FunctionType(p):
    """FunctionType : KW_FUNC Signature"""


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
        input_code = f.read()
        if input_code[len(input_code) - 1] != "\n":
            input_code += "\n"
        go_lexer.input_code = input_code
        lines = input_code.split("\n")
        go_lexer.lines = lines
        utils.lines = lines
        result = parser.parse(input_code, tracking=True, debug=False)
        # print(result)

        ast = syntree.optimize_AST(ast)
        draw_AST(ast)

        # Intermediate Code gen
        ic = intermediate_codegen(ast)

        with open("syntax_tree.txt", "wt", encoding="utf-8") as ast_file:
            sys.stdout = ast_file
            print_tree(ast, nameattr=None, horizontal=True)
            sys.stdout = sys.__stdout__

        print("Finished Parsing!")
        print("Symbol Table: ")
        print(symtab)
        with open("symbol_table.txt", "wt", encoding="utf-8") as symtab_file:
            print(symtab, file=symtab_file)

        #  print("Type Table: ")
        #  print(type_table)

        print("Intermediate code:")
        # ic.print_three_address_code()
        print(ic)
