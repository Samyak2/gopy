from typing import Optional

from go_lexer import symtab


class Node:
    """Node of an AST

    Warning: pls don't change the children values after setting them
    for nodes which depend on it"""

    def __init__(self, name, **kwargs):
        self.name = name
        self.children: list = [c for c in kwargs["children"] if c is not None]
        self.data = kwargs.get("data", None)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.data is not None:
            return f"<{self.name}: {str(self.data)}>"
        else:
            return f"<{self.name}>"

    def add_child(self, child):
        if child is not None:
            self.children.append(child)


class BinOp(Node):
    """Node for binary operations"""

    def __init__(self, operator, left=None, right=None):
        super().__init__(f"Binary {operator}", children=[left, right], data=operator)
        self.operator = self.data
        self.left = left
        self.right = right


class Assignment(BinOp):
    """Node for assignment operations"""


class UnaryOp(Node):
    """Node for unary operations"""

    def __init__(self, operator, operand):
        if isinstance(operand, UnaryOp) and operand.operator is None:
            operand = operand.operand
        super().__init__(f"Unary {operator}", children=[operand], data=operator)
        self.operand = operand
        self.operator = operator


class PrimaryExpr(Node):
    """Node for PrimaryExpr

    Ref: https://golang.org/ref/spec#PrimaryExpr
    """

    def __init__(self, operand, children=None):
        super().__init__(
            "PrimaryExpr", children=[] if children is None else children, data=operand
        )


class Literal(Node):
    """Node to store literals"""

    def __init__(self, type_, data):
        super().__init__(f"{type_} literal", children=[], data=(type_, data))
        self.type_ = type_
        self.data = data


class Import(Node):
    """Node to store imports"""

    def __init__(self, pkg_name, import_path):
        super().__init__("import", children=[], data=(pkg_name, import_path))


class List(Node):
    """Node to store literals"""

    def __init__(self, children):
        super().__init__("LIST", children=children)
        self.append = self.add_child

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)


class Arguments(Node):
    """Node to store function arguments"""

    def __init__(self, expression_list):
        super().__init__("arguments", children=[expression_list])
        self.expression_list = expression_list


class Signature(Node):
    """Node to store function signature"""

    def __init__(self, parameters, result=None):
        super().__init__("signature", children=[parameters, result])
        self.parameters = parameters
        self.result = result


class Function(Node):
    """Node to store function declaration"""

    def __init__(self, name, signature, lineno: int, body=None):
        super().__init__("FUNCTION", children=[signature, body], data=(name, lineno))
        self.data: tuple
        if name is not None:
            symtab.declare_new_variable(
                name[1], lineno, 0, type_="FUNCTION", const=True, value=self
            )

        self.fn_name = name
        self.lineno = lineno
        self.signature = signature
        self.body = body


class Type(Node):
    """Parent class for all types"""


class Array(Type):
    """Node for an array type"""

    def __init__(self, eltype, length):
        super().__init__("ARRAY", children=[length], data=eltype)
        self.eltype = eltype
        self.length = length


class Identifier(Node):
    """Node for identifiers"""

    def __init__(self, ident_tuple, lineno):
        super().__init__(
            "IDENTIFIER", children=[], data=(ident_tuple[1], lineno, ident_tuple[2])
        )
        symtab.add_if_not_exists(ident_tuple[1])
        self.ident_name = ident_tuple[1]
        self.lineno = lineno
        self.col_num = ident_tuple[2]


class QualifiedIdent(Node):
    """Node for qualified identifiers"""

    def __init__(self, package_name, identifier):
        super().__init__("IDENTIFIER", children=[], data=(package_name, identifier))


class VariableDecl(Node):
    """Node to store variable and constant declarations"""

    def __init__(
        self,
        identifier_list: List,
        type_=None,
        expression_list: Optional[List] = None,
        const: bool = False,
    ):
        super().__init__(
            "DECL",
            children=[identifier_list, expression_list],
            data=(type_, const),
        )

        if expression_list is None:
            # TODO: implement default values
            ident: Identifier
            for ident in identifier_list:
                symtab.declare_new_variable(
                    ident.ident_name,
                    ident.lineno,
                    ident.col_num,
                    type_=type_,
                    const=const,
                )
        elif len(identifier_list) == len(expression_list):
            ident: Identifier
            expr: Node
            for ident, expr in zip(identifier_list, expression_list):
                # TODO: check value is appropriate for type
                symtab.declare_new_variable(
                    ident.ident_name,
                    ident.lineno,
                    ident.col_num,
                    type_=type_,
                    value=expr,
                    const=const,
                )
        else:
            raise NotImplementedError("Declaration with unpacking not implemented yet")

        self.expression_list = expression_list
        self.identifier_list = identifier_list
        self.type_ = type_
        self.is_const = const


class ParameterDecl(Node):
    def __init__(self, type_, vararg=False, ident_list=None):
        super().__init__("PARAMETERS", children=[type_, ident_list], data=vararg)
        self.type_ = type_
        self.vararg = vararg
        self.ident_list = ident_list
        if ident_list is not None:
            self.var_decl = VariableDecl(ident_list)


class IfStmt(Node):
    def __init__(self, body, expr, statement=None, next_=None):
        super().__init__("IF", children=[statement, expr, body, next_])
        self.statement = statement
        self.expr = expr
        self.body = body
        self.next_ = next_


class ForStmt(Node):
    def __init__(self, body, clause=None):
        super().__init__("FOR", children=[body, clause])
        self.body = body
        self.clause = clause


class ForClause(Node):
    def __init__(self, init, cond, post):
        super().__init__("FOR_CLAUSE", children=[init, cond, post])
        self.init = init
        self.cond = cond
        self.post = post


class RangeClause(Node):
    def __init__(self, expr, ident_list=None, expr_list=None):
        if ident_list is not None:
            self.var_decl = VariableDecl(ident_list, expr)
        else:
            self.var_decl = None
        super().__init__("RANGE", children=[expr, ident_list, expr_list, self.var_decl])
        self.expr = expr
        self.ident_list = ident_list
        self.expr_list = expr_list


#     def print_level_order(self):

#         queue = []

#         queue.append(self)

#         while queue:

#             node = queue.pop(0)
#             Node.print_node(node)

#             if isinstance(node, Node):
#                 queue.extend(node.children)
