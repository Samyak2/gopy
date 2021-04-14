from symbol_table import SymbolInfo
from typing import Any, Optional
import traceback

from go_lexer import symtab, type_table
from utils import print_error, print_line, print_marker, lines


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

    def data_str(self) -> str:
        return "" if self.data is None else str(self.data)

    def add_child(self, child):
        if child is not None:
            self.children.append(child)


class BinOp(Node):
    """Node for binary operations"""

    def __init__(self, operator, left=None, right=None, type_=None, lineno=None):
        super().__init__("Binary", children=[left, right], data=operator)
        self.operator = self.data
        self.left = left
        self.right = right
        self.lineno = lineno

        self.type_ = None
        try:

            def get_type(child: Node) -> str:

                if isinstance(child, PrimaryExpr):
                    if len(child.children) > 0 and isinstance(child.children[0], Index):
                        x = symtab.get_symbol(child.data[1]).type_.eltype

                    else:
                        x = symtab.get_symbol(child.data[1]).type_.name

                elif hasattr(child, "type_"):
                    x = getattr(child, "type_")

                else:
                    raise Exception("Could not determine type of child", child)

                return x

            x = get_type(self.children[0])
            y = get_type(self.children[1])

            def check_type(x, y):
                if x == "int":
                    if y == "float64":
                        self.type_ = "float64"
                        return 1

                return 0

            if x != y:
                val1 = check_type(x, y)
                val2 = check_type(y, x)
                if (
                    not isinstance(self.children[0], Literal)
                    and not isinstance(self.children[1], Literal)
                ) or not (val1 | val2):
                    print_error(
                        "Type Mismatch",
                        kind="TYPE ERROR",
                    )
                    print(
                        f"Cannot apply operation {self.operator}"
                        f" on types {x} and {y}"
                    )
                    print_line(self.lineno)
                    print_marker(0, len(lines[self.lineno - 1]))

            else:
                self.type_ = x
        except Exception:
            traceback.format_exc()


class Assignment(BinOp):
    """Node for assignment operations"""


class UnaryOp(Node):
    """Node for unary operations"""

    def __init__(self, operator, operand):
        if isinstance(operand, UnaryOp) and operand.operator is None:
            operand = operand.operand

        super().__init__("Unary", children=[operand], data=operator)
        self.operand = operand
        self.operator = operator
        self.type_ = None

        if hasattr(operand, "type_"):
            self.type_ = operand.type_
        else:
            self.type_ = operand.data[0]


class PrimaryExpr(Node):
    """Node for PrimaryExpr

    Ref: https://golang.org/ref/spec#PrimaryExpr
    """

    def __init__(self, operand, children=None):
        # small optimization for the case when PrimaryExpr
        # has children of [PrimaryExpr, something]
        # with PrimaryExpr having only data and no children
        if operand is None and children is not None:
            if len(children) == 2 and isinstance(children[0], PrimaryExpr):
                if children[0].children is None or children[0].children == []:
                    operand = children[0].data
                    children = children[1:]

        super().__init__(
            "PrimaryExpr", children=[] if children is None else children, data=operand
        )
        self.ident: Optional[SymbolInfo] = symtab.get_symbol(
            operand[1] if isinstance(operand, tuple) else ""
        )

    def data_str(self):
        # self.data can be an IDENTIFIER sometimes, so just show the name
        if isinstance(self.data, tuple) and self.data[0] == "identifier":
            return f"identifier: {self.data[1]}"
        else:
            return super().data_str()


class Literal(Node):
    """Node to store literals"""

    def __init__(self, type_, value):
        children = []
        if isinstance(type_, Node):
            children.append(type_)

        super().__init__("LITERAL", children=children, data=(type_, value))

        self.type_ = type_
        self.value = value

    def data_str(self):
        return f"type: {self.type_}, value: {self.value}"


class Import(Node):
    """Node to store imports"""

    def __init__(self, pkg_name, import_path):
        # import_path is a STRING_LIT, so it has ("string", value)
        super().__init__("import", children=[], data=(pkg_name, import_path))

    def data_str(self):
        return f"name: {self.data[0]}, path: {self.data[1][1]}"


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


class FunctionCall(Node):
    """Node for a function call

    Is a part of PrimaryExpr in the grammar, but separated here"""

    def __init__(self, fn_name: Any, arguments: Arguments):
        if (
            isinstance(fn_name, PrimaryExpr)
            and isinstance(fn_name.data, tuple)
            and fn_name.data[0] == "identifier"
        ):
            fn_name = str(fn_name.data[1])

        self.fn_name = fn_name
        self.arguments = arguments

        super().__init__("FunctionCall", children=[arguments], data=fn_name)

    @staticmethod
    def get_fn_name(fn_name) -> str:
        if isinstance(fn_name, QualifiedIdent):
            return f"{fn_name.data[0][1]}__{fn_name.data[1][1]}"
        elif isinstance(fn_name, tuple) and fn_name[0] == "identifier":
            return fn_name[1]
        elif isinstance(fn_name, str):
            return fn_name
        else:
            raise Exception(
                "Function call name could not be determined from fn_name " f"{fn_name}"
            )

    def data_str(self):
        if isinstance(self.fn_name, QualifiedIdent):
            return self.fn_name.data_str()
        return self.fn_name


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
            # self.add_func_to_symtab(name[1], lineno, self)
            # symtab.declare_new_variable(
            #     name[1], lineno, 0, type_="FUNCTION", const=True, value=self
            # )
            symtab.update_info(
                name[1], lineno, 0, type_="FUNCTION", const=True, value=self
            )

        self.fn_name = name
        self.lineno = lineno
        self.signature = signature
        self.body = body

    @staticmethod
    def add_func_to_symtab(name, lineno, value=None):
        symtab.declare_new_variable(
            name, lineno, 0, type_="FUNCTION", const=True, value=value
        )

    def data_str(self):
        return f"name: {self.fn_name}, lineno: {self.lineno}"


class Keyword(Node):
    """Node to store a single keyword - like return, break, continue, etc."""

    def __init__(self, kw, ext=None, children=None):
        self.kw = kw
        self.ext = ext if ext is not None else ()
        children = [] if children is None else children

        super().__init__(kw, children=children, data=(kw, *self.ext))

    def data_str(self):
        return ""


class Type(Node):
    """Parent class for all types"""


class Array(Type):
    """Node for an array type"""

    def __init__(self, eltype, length):
        super().__init__("ARRAY", children=[length], data=eltype)
        eltype = eltype.data
        self.eltype = eltype
        self.length = length

        # if hasattr(eltype, "type_"):
        #     storage = self.length * type_table.get_type(eltype.type_).storage
        # else:
        #     storage = None
        storage = self.length.value * type_table.get_type(eltype).storage

        self.typename = f"ARRAY_{eltype}"
        type_table.add_type(
            self.typename,
            lineno=None,
            col_num=None,
            storage=storage,
            eltype=eltype,
            check=False,
        )

    def data_str(self):
        return f"eltype: {self.eltype}"


class Slice(Type):
    """Node for a slice type"""

    def __init__(self, eltype):
        super().__init__("SLICE", children=[], data=eltype)
        eltype = eltype.data
        self.eltype = eltype
        self.typename = f"SLICE_{eltype}"
        type_table.add_type(
            self.typename,
            lineno=None,
            col_num=None,
            storage=None,
            eltype=eltype,
            check=False,
        )

    def data_str(self):
        return f"eltype: {self.eltype}"


class Index(Node):
    """Node for array/slice indexing"""

    def __init__(self, expr):
        super().__init__("INDEX", children=[expr], data=None)

        self.expr = expr


class Identifier(Node):
    """Node for identifiers"""

    def __init__(self, ident_tuple, lineno):
        super().__init__(
            "IDENTIFIER", children=[], data=(ident_tuple[1], lineno, ident_tuple[2])
        )
        # symtab.add_if_not_exists(ident_tuple[1])
        self.ident_name = ident_tuple[1]
        self.lineno = lineno
        self.col_num = ident_tuple[2]

    def add_symtab(self):
        symtab.add_if_not_exists(self.ident_name)

    def data_str(self):
        return f"name: {self.ident_name}, lineno: {self.lineno}"


class QualifiedIdent(Node):
    """Node for qualified identifiers"""

    def __init__(self, package_name, identifier):
        super().__init__("IDENTIFIER", children=[], data=(package_name, identifier))

    def data_str(self):
        return f"package: {self.data[0][1]}, name: {self.data[1][1]}"


class VarDecl(Node):
    """Node to store one variable or const declaration"""

    def __init__(self, ident: Identifier, type_=None, value=None, const: bool = False):
        self.ident = ident
        self.type_ = type_
        self.value = value
        self.const = const
        self.symbol: Optional[SymbolInfo] = symtab.get_symbol(self.ident.ident_name)

        children = []

        if isinstance(type_, Node):
            children.append(type_)
        else:
            children.append(List([]))

        if isinstance(value, Node):
            children.append(value)
        else:
            children.append(List([]))

        super().__init__(
            name="DECL", children=children, data=(ident, type_, value, const)
        )

    def data_str(self):
        s = f"name: {self.ident.ident_name}"

        if not isinstance(self.type_, Node) and self.type_ is not None:
            s += f", type: {self.type_}"

        if not isinstance(self.value, Node) and self.value is not None:
            s += f", value: {self.value}"

        s += f", is_const: {self.const}"

        return s


def make_variable_decls(
    identifier_list: List,
    type_=None,
    expression_list: Optional[List] = None,
    const: bool = False,
):
    var_list = List([])

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
            var_list.append(VarDecl(ident, type_, const=const))
    elif len(identifier_list) == len(expression_list):
        ident: Identifier
        expr: Node
        for ident, expr in zip(identifier_list, expression_list):
            # type inference
            inf_type = "unknown"
            if isinstance(expr, BinOp) or isinstance(expr, UnaryOp):
                inf_type = expr.type_
            elif isinstance(expr, Literal):
                inf_type = expr.type_
            else:
                print("Could not determine type: ", ident, expr)

            if inf_type is None:
                inf_type = "unknown"

            inf_typename = get_typename(inf_type)

            # now check if the LHS and RHS types match
            if type_ is None:
                type_ = inf_type
            else:
                # get just the type name
                typename = get_typename(type_)

                if typename != inf_typename:
                    # special case for literal
                    if not isinstance(expr, Literal):
                        print_error("Type Mismatch", kind="TYPE ERROR")
                        print(
                            f"Cannot use expression of type {inf_typename} as "
                            f"assignment to type {typename}"
                        )
                        print_line(ident.lineno)
                        print_marker(0, len(lines[ident.lineno - 1]))

            symtab.declare_new_variable(
                ident.ident_name,
                ident.lineno,
                ident.col_num,
                type_=type_,
                value=expr,
                const=const,
            )
            #  print(type_)

            var_list.append(VarDecl(ident, type_, expr, const))
            #  Most important line
            type_ = None
    else:
        raise NotImplementedError("Declaration with unpacking not implemented yet")

    return var_list


class ParameterDecl(Node):
    def __init__(self, type_, vararg=False, ident_list=None):
        super().__init__("PARAMETERS", children=[type_, ident_list], data=vararg)
        self.type_ = type_
        self.vararg = vararg
        self.ident_list = ident_list
        if ident_list is not None:
            self.var_decl = make_variable_decls(ident_list, type_=type_)

    def data_str(self):
        return f"is_vararg: {self.vararg}"


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
            self.var_decl = make_variable_decls(ident_list, expr)
        else:
            self.var_decl = None
        super().__init__("RANGE", children=[expr, ident_list, expr_list, self.var_decl])
        self.expr = expr
        self.ident_list = ident_list
        self.expr_list = expr_list


class Struct(Type):
    def __init__(self, field_decl_list):
        self.fields = []

        for i in field_decl_list:
            i: StructFieldDecl
            if i.ident_list is not None:
                for ident in i.ident_list:
                    ident: Identifier
                    self.fields.append(StructField(ident.ident_name, i.type_, i.tag))
            elif i.embed_field is not None:
                # TODO: handle pointer type here
                self.fields.append(StructField(i.embed_field[1], None, i.tag))

        super().__init__("Struct", children=self.fields)


class StructField(Node):
    def __init__(self, name, type_, tag):
        self.f_name = name
        self.type_ = type_
        self.tag = tag

        super().__init__("StructField", children=[type_], data=(name, type_, tag))

    def data_str(self):
        return f"name: {self.f_name}, type: {self.type_}, tag: {self.tag}"


class StructFieldDecl:
    def __init__(self, ident_list_or_embed_field, type_=None, tag=None):
        if isinstance(ident_list_or_embed_field, List):
            self.ident_list = ident_list_or_embed_field
            self.embed_field = None
        else:
            self.embed_field = ident_list_or_embed_field
            self.ident_list = None

        self.type_ = type_
        self.tag = tag


class TypeDef(Node):
    def __init__(self, typename, type_: Type, type_table, lineno):
        self.typename = typename
        self.type_ = type_

        super().__init__(name="TypeDef", children=[type_], data=typename)

        type_table.add_type(typename[1], lineno, typename[2], None)


def get_typename(type_) -> str:
    """Returns just the typename from given type"""
    if isinstance(type_, str):
        return type_
    if isinstance(type_, Array) or isinstance(type_, Slice):
        return type_.typename
    if isinstance(type_, Struct):
        raise NotImplementedError("Type name for struct not supported yet")
    if isinstance(type_, Type):
        return str(type_.data)

    raise Exception("Could not determine type from given:", type_)


def _optimize(node: Node) -> Node:
    num_list_childs = 0

    for i, child in enumerate(node.children):
        if isinstance(child, List):
            num_list_childs += 1

            # if List has only one child, remove the list
            if len(child) == 1:
                node.children[i] = child.children[0]
                if not isinstance(node.children[i], List):
                    num_list_childs -= 1

    # if List has all List children, flatten out the nesting
    if isinstance(node, List) and num_list_childs == len(node.children):
        new_children = List([])

        for child in node.children:
            child: List
            for child_child in child.children:
                new_children.append(child_child)

        node = new_children

    for i, child in enumerate(node.children):
        node.children[i] = _optimize(child)

    return node


def optimize_AST(ast: Node):
    return _optimize(ast)
