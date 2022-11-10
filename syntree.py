import traceback

from symbol_table import SymbolInfo
from typing import Any, Optional, Tuple, Union
from go_lexer import symtab
from utils import (
    print_error,
    print_line,
    print_line_marker_nowhitespace,
    print_marker,
)


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


class Identifier(Node):
    """Node for identifiers"""

    def __init__(self, ident_tuple, lineno):
        super().__init__("IDENTIFIER",
                         children=[],
                         data=(ident_tuple[1], lineno, ident_tuple[2]))
        # symtab.add_if_not_exists(ident_tuple[1])
        self.ident_name = ident_tuple[1]
        self.lineno = lineno
        self.col_num = ident_tuple[2]

    def add_symtab(self):
        symtab.add_if_not_exists(self.ident_name)

    def data_str(self):
        return f"name: {self.ident_name}, lineno: {self.lineno}"


class BinOp(Node):
    """Node for binary operations"""

    rel_ops = {"==", "!=", "<", ">", "<=", ">="}
    logical_ops = {"&&", "||"}

    def __init__(self, operator, left=None, right=None, lineno=None):
        super().__init__("Binary", children=[left, right], data=operator)
        self.operator = self.data
        self.left = left
        self.right = right
        self.lineno = lineno

        self.is_relop = self.operator in self.rel_ops
        self.is_logical = self.operator in self.logical_ops

        self.type_: str = None

        try:
            def get_type(expr: Node) -> str:
                infered_type = infer_expr_typename(expr)
                if infered_type is None:
                    raise Exception(f"type inference failed on expression '{expr}: {type(expr)}'")

                return infered_type

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
                if ((not isinstance(self.children[0], Literal)
                    and not isinstance(self.children[1], Literal))
                    or not (val1 | val2)):
                    print_error(
                        "Type Mismatch",
                        kind="TYPE ERROR",
                    )
                    print(f"Cannot apply operation {self.operator}"
                          f" on types {x} and {y}")
                    print_line_marker_nowhitespace(self.lineno)

                if self.is_relop:
                    self.type_ = "bool"

            else:
                if self.is_relop:
                    self.type_ = "bool"

                elif self.is_logical:
                    if x == "bool":
                        self.type_ = "bool"
                    else:
                        print_error("Invalid Operation", kind="Operation Error")

                else:
                    self.type_ = x

        except Exception:
            print(traceback.format_exc())


class Assignment(BinOp):
    """Node for assignment operations"""

    def __init__(self, operator, left=None, right=None, lineno=None):
        if isinstance(left, List) and len(left.children) == 1 and isinstance(left.children[0], PrimaryExpr):
            left_ = left.children[0]
            if left_.ident is not None:
                if left_.ident.const:
                    print_error("Constant assignment")
                    print(f"Constant {left_.ident.name} cannot be assigned to")
                    print_line_marker_nowhitespace(lineno)

        super().__init__(operator, left, right, lineno)


class UnaryOp(Node):
    """Node for unary operations"""

    def __init__(self, operator, operand, lineno: int):
        if isinstance(operand, UnaryOp) and operand.operator is None:
            operand = operand.operand

        super().__init__("Unary", children=[operand], data=operator)
        self.operand = operand
        self.operator = operator
        self.type_ = None
        self.lineno = lineno

        if hasattr(operand, "type_"):
            self.type_ = operand.type_
        else:
            self.type_ = operand.data[0]

        if self.type_ == "string":
            print_error("Type Error", kind="Invalid Operation")

        if self.operator == '!' and self.type_ != "bool":
            print_error("Type Error", kind="Invalid Operation")


class PrimaryExpr(Node):
    """Node for PrimaryExpr

    Ref: https://golang.org/ref/spec#PrimaryExpr
    """

    def __init__(self, operand, lineno: int, children=None):
        # small optimization for the case when PrimaryExpr
        # has children of [PrimaryExpr, something]
        # with PrimaryExpr having only data and no children
        if operand is None and children is not None:
            if len(children) == 2 and isinstance(children[0], PrimaryExpr):
                if children[0].children is None or children[0].children == []:
                    operand = children[0].data
                    children = children[1:]

        super().__init__("PrimaryExpr",
                         children=[] if children is None else children,
                         data=operand)
        self.ident: Optional[SymbolInfo] = symtab.get_symbol(
            operand[1] if isinstance(operand, tuple) else "")
        self.lineno = lineno

    @property
    def operand(self) -> tuple:
        return self.data

    @property
    def col_no(self):
        return self.operand[-1]

    def data_str(self):
        # self.data can be an IDENTIFIER sometimes, so just show the name
        if isinstance(self.data, tuple) and self.data[0] == "identifier":
            return f"identifier: {self.data[1]}"
        else:
            return super().data_str()


class Literal(Node):
    """Node to store literals"""

    def __init__(self, type_, value, lineno: int):
        children = []
        if isinstance(type_, Node):
            children.append(type_)

        if isinstance(value, Node):
            children.append(value)

        super().__init__("LITERAL", children=children, data=(type_, value))

        self.type_ = type_
        self.value = value
        self.lineno = lineno

    def data_str(self):
        return f"type: {self.type_}, value: {self.value}"

    def __str__(self):
        return str(self.value)


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
        pos = fn_name.lineno, fn_name.col_no

        if (isinstance(fn_name, PrimaryExpr) and
                isinstance(fn_name.data, tuple) and
                fn_name.data[0] == "identifier"):
            fn_name = str(fn_name.data[1])

        self.fn_name = fn_name
        self.arguments = arguments
        expression_list = arguments.expression_list
        if expression_list is None:
            expression_list = []

        self.fn_sym = symtab.get_symbol(str(fn_name))
        if self.fn_sym is not None:
            parameters = self.fn_sym.type_.signature.parameters
            param_decls = []  # list of types in declared order
            for para in parameters:
                para_list: List[VarDecl] = [
                    decl for decl in para.var_decl
                ]
                para_list.reverse()
                param_decls.extend(para_list)

            expected_count = len(param_decls)
            recieved_count = len(expression_list)
            if recieved_count != expected_count:
                print_error("Arguments Number Mismatch Declaration", kind="TYPE ERROR")
                tense = "were" if recieved_count > 1 else "was"
                err_msg = (f"{fn_name}() takes {expected_count} arguments"
                           f" but {recieved_count} {tense} given")
                print_func_err(pos, len(fn_name), err_msg)
            else:
                param_decls.reverse()  # to match order of expression_list
                for arg, param_decl in zip(expression_list, param_decls):
                    arg_type = infer_expr_typename(arg)
                    data = arg.data
                    para_type = param_decl.symbol.type_.typename
                    if arg_type != para_type:
                        print_error("Arguments Type Mismatch Declaration", kind="TYPE ERROR")
                        exp = data
                        if isinstance(data, tuple):
                            exp = data[1]
                        err_msg_call = (f"{exp} has type {arg_type}")
                        err_msg_decl = f"but function wanted {para_type}"
                        print_func_err(
                            pos,
                            len(fn_name),
                            err_msg_call,
                            err_msg_decl,
                            param_decl.ident
                        )

        self.type_ = None
        if self.fn_sym is not None:
            if self.fn_sym.value is not None:
                self.type_ = self.fn_sym.value.signature.ret_type

        super().__init__("FunctionCall", children=[arguments], data=fn_name)


def print_func_err(
    pos: Tuple[int, int],
    width: int,
    err_msg_call: str,
    err_msg_decl: Optional[str] = None,
    param_ident: Optional[Identifier] = None
):
    line_no = pos[0]
    col_no = pos[1]
    print(err_msg_call)
    print_line(line_no)
    print_marker(col_no - 1, width)
    if param_ident is not None:
        print(err_msg_decl)
        print_line(param_ident.lineno)
        print_marker(param_ident.col_num - 1, len(param_ident.ident_name))

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
                "Function call name could not be determined from fn_name "
                f"{fn_name}")

    def data_str(self):
        if isinstance(self.fn_name, QualifiedIdent):
            return self.fn_name.data_str()
        return self.fn_name


class Signature(Node):
    """Node to store function signature"""

    def __init__(self, parameters, result=None):
        self.parameters = parameters
        self.result = result

        self.ret_type = None
        if self.result is not None:
            self.ret_type = infer_expr_typename(self.result)

        super().__init__("signature", children=[parameters, result])


class Function(Node):
    """Node to store function declaration"""

    def __init__(self, name: Optional[tuple], signature, lineno: int, body=None):
        super().__init__("FUNCTION",
                         children=[signature, body],
                         data=(name, lineno))
        self.data: tuple

        self.fn_name = name
        self.lineno = lineno
        self.signature = signature
        self.body = body

        if name is not None:
            symtab.update_info(name[1],
                               lineno,
                               0,
                               type_= FunctionType(signature),
                               const=True,
                               value=self)

    @staticmethod
    def add_func_to_symtab(name, lineno, value=None):
        sig = Signature(List([]))
        symtab.declare_new_variable(name,
                                    lineno,
                                    0,
                                    type_=FunctionType(sig),
                                    const=True,
                                    value=value)

    def data_str(self):
        return f"name: {self.fn_name}, lineno: {self.lineno}"


def infer_expr_typename(expr: Union[
        BinOp | UnaryOp | PrimaryExpr | Function | Type | FunctionCall
    ]) -> Optional[str]:
    """performance type inference on expr returns optional string representing typename
    """
    if isinstance(expr, Type):
        return expr.typename

    elif isinstance(expr, BinOp):
        return expr.type_

    elif isinstance(expr, UnaryOp):
        return expr.type_

    elif isinstance(expr, FunctionCall):
        fn_name_info = symtab.get_symbol(expr.fn_name)
        return fn_name_info.type_.ret_typename

    elif isinstance(expr, Literal):
        lit_type = expr.type_
        return getattr(lit_type, "typename", lit_type)

    elif isinstance(expr, Function):
        return FunctionType.get_func_typename(expr.signature)

    elif isinstance(expr, PrimaryExpr):
        if (len(expr.children) > 0 and isinstance(expr.children[0], Index)):
            # primaryExp[Index]
            # operand: primaryExpr, children[0]: Index
            return symtab.get_symbol(expr.data[1]).type_.eltype.typename

        else:
            # identifier
            return symtab.get_symbol(expr.data[1]).type_.typename

    return None


class Keyword(Node):
    """Node to store a single keyword - like return, break, continue, etc."""

    def __init__(self, kw, ext=None, children=None, lineno=None):
        self.kw = kw
        self.ext = ext if ext is not None else ()
        self.lineno = lineno
        children = [] if children is None else children

        super().__init__(kw, children=children, data=(kw, *self.ext))

    def data_str(self):
        return ""


class Type(Node):
    """Parent class for all types"""

    def __init__(
        self,
        type_class: str,
        typename: str,
        storage: Optional[int] = None
    ):
        # type_class could be ARRAY, SLICE, FUNCTION, BasicType
        self.typename = typename
        self.storage = storage
        super().__init__(type_class, children=[], data=typename)

    def __str__(self):
        return f"<{self.typename}>"


class FunctionType(Type):
    """Node for FunctionType"""

    def __init__(self, signature: Signature):
        assert signature is not None
        self.signature = signature
        self.ret_typename: str = FunctionType.get_ret_typename(self.signature)
        typename = FunctionType.get_func_typename(self.signature)
        super().__init__("FUNCTION", typename)

    @staticmethod
    def get_ret_typename(signature: Signature) -> str:
        if signature.result is not None:
            return infer_expr_typename(signature.result)
        return ""

    @staticmethod
    def get_func_typename(signature: Signature) -> str:
        para_types: List[str] = []
        for para in signature.parameters:
            ellipsis: str = "..." if para.vararg else ""
            if para.ident_list is None:
                typename: str = f"{ellipsis}{para.type_.typename}"
                para_types.append(typename)
            else:
                for para_decl in para.var_decl:
                    typename: str = f"{ellipsis}{para_decl.type_.typename}"
                    para_types.append(typename)

        func_typename = "func("
        for typename in para_types:
            func_typename = f"{func_typename}{typename}, "

        if para_types != []:
            # replace last comma with parenthesis
            func_typename = func_typename[:-2] + ") "
        else:
            func_typename = "func()"

        ret_type = FunctionType.get_ret_typename(signature)
        return f"{func_typename}{ret_type}"


class Array(Type):
    """Node for an array type"""

    def __init__(self, eltype, length):
        self.eltype = eltype
        self.length = length.value

        eltype_info = symtab.get_symbol(eltype.typename)
        if eltype_info is None:
            # TODO: handle error
            ...

        eltype_storage = eltype_info.value.storage
        storage = self.length * eltype_storage
        typename = f"ARRAY_[{self.length}]{eltype.typename}"
        super().__init__("ARRAY", typename, storage)

    def data_str(self):
        return f"eltype: {self.eltype.typename}"


class Slice(Type):
    """Node for a slice type"""

    def __init__(self, eltype):
        self.eltype = eltype
        typename = f"SLICE_{self.eltype.typename}"
        super().__init__("SLICE", typename, storage=None)

    def data_str(self):
        return f"eltype: {self.eltype.typename}"


def infer_expr_type(expr: Union[Node | str]) -> Optional[
        Union[Type | Array | Slice | FunctionType]
    ]:

    if isinstance(expr, Type):
        return expr

    infered_type: Union[str | Type | Array | Slice | FunctionType] = None

    if isinstance(expr, (BinOp, UnaryOp, Literal)):
        infered_type = expr.type_
        if isinstance(infered_type, str):
            type_info = symtab.get_symbol(infered_type)
            if type_info is not None and hasattr(type_info.value, "storage"):
                infered_type = type_info.value

    elif isinstance(expr, FunctionCall):
        fn_name_info = symtab.get_symbol(expr.fn_name)
        if fn_name_info is not None:
            infered_type = fn_name_info.type_.signature.result

    elif isinstance(expr, Function):
        infered_type = FunctionType(expr.signature)

    elif isinstance(expr, str):
        type_info = symtab.get_symbol(infered_type)
        if type_info is not None and hasattr(type_info.type_, "storage"):
            infered_type = type_info.type_

    elif isinstance(expr, PrimaryExpr):
        if len(expr.children) > 0 and isinstance(expr.children[0], Index):
            # primaryExp[Index]
            # operand: primaryExpr, children[0]: Index
            infered_type = symtab.get_symbol(expr.data[1]).type_.eltype

        else:
            # identifier
            infered_type = symtab.get_symbol(expr.data[1]).type_

    if isinstance(infered_type, (Array, Type, Slice, FunctionType)):
        return infered_type

    return None


class Index(Node):
    """Node for array/slice indexing"""

    def __init__(self, expr):
        super().__init__("INDEX", children=[expr], data=None)

        self.expr = expr


class QualifiedIdent(Node):
    """Node for qualified identifiers"""

    def __init__(self, package_name, identifier, lineno: int):
        super().__init__("IDENTIFIER",
                         children=[],
                         data=(package_name, identifier))
        self.lineno = lineno

    @property
    def col_no(self) -> int:
        self.data[-1][-1]

    def data_str(self):
        return f"package: {self.data[0][1]}, name: {self.data[1][1]}"


class VarDecl(Node):
    """Node to store one variable or const declaration"""

    def __init__(self,
                 ident: Identifier,
                 type_=None,
                 value=None,
                 const: bool = False):
        self.ident = ident
        self.type_ = type_
        self.value = value
        self.const = const
        self.symbol: Optional[SymbolInfo] = symtab.get_symbol(
            self.ident.ident_name)

        children = []

        if isinstance(type_, Node):
            children.append(type_)
        else:
            children.append(List([]))

        if isinstance(value, Node):
            children.append(value)
        else:
            children.append(List([]))

        super().__init__(name="DECL",
                         children=children,
                         data=(ident, type_, value, const))

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

        orig_type = type_

        for ident, expr in zip(identifier_list, expression_list):
            # type inference
            inf_type = infer_expr_type(expr)
            if inf_type is None:
                print(f"WARNING: failed to deduce type of expression {expr}: {type(expr)}")
                inf_type = "unknown"

            inf_typename = infer_expr_typename(inf_type)

            # now check if the LHS and RHS types match
            if type_ is None:
                type_ = inf_type
            else:
                # get just the type name
                typename = infer_expr_typename(type_)

                if typename != inf_typename:
                    # special case for literal
                    # Question: what's with this special case?
                    if not isinstance(expr, Literal):
                        print_error("Type Mismatch", kind="TYPE ERROR")
                        print(
                            f"Cannot use expression of type {inf_typename} as "
                            f"assignment to type {typename}")
                        print_line_marker_nowhitespace(ident.lineno)

            symtab.declare_new_variable(
                ident.ident_name,
                ident.lineno,
                ident.col_num,
                type_=type_,
                value=expr,
                const=const,
            )

            var_list.append(VarDecl(ident, type_, expr, const))
            type_ = orig_type
    else:
        raise NotImplementedError(
            "Declaration with unpacking not implemented yet")

    return var_list


class ParameterDecl(Node):

    def __init__(self, type_, vararg=False, ident_list=None):
        super().__init__("PARAMETERS",
                         children=[type_, ident_list],
                         data=vararg)
        self.type_ = type_
        self.vararg = vararg
        self.ident_list = ident_list
        if ident_list is not None:
            self.var_decl = make_variable_decls(ident_list, type_=type_)

    def data_str(self):
        return f"is_vararg: {self.vararg}"


class IfStmt(Node):

    def __init__(self, body, expr, statement=None, next_=None, lineno=None):
        super().__init__("IF", children=[statement, expr, body, next_])
        self.statement = statement
        self.expr = expr
        self.body = body
        self.next_ = next_

        self.lineno = lineno

        # signal the AST optimizer to not optimize these children
        self._no_optim = True

        if isinstance(self.expr, BinOp):
            if self.expr.type_ != "bool":
                print_error("Invalid operator in condition", kind="ERROR")
                print("Cannot use non-boolean binary operator "
                      f"{self.expr.operator}"
                      " in a condition")
                print_line_marker_nowhitespace(lineno)
        elif hasattr(self.expr, "type_") and getattr(self.expr, "type_") != "bool":
            print_error("Invalid condition", kind="TYPE ERROR")
            print("Cannot use non-binary expression in condition")
            print_line_marker_nowhitespace(lineno)


class ForStmt(Node):

    def __init__(self, body, clause, lineno):
        super().__init__("FOR", children=[body, clause])
        self.body = body
        self.clause = clause
        self.lineno = lineno

        # signal the AST optimizer to not optimize these children
        self._no_optim = True

        if hasattr(clause, "type_") and getattr(clause, "type_") == "bool":
            pass
        elif isinstance(clause, ForClause):
            pass
        else:
            print_error("Invalid condition", kind="TYPE ERROR")
            print("Cannot use non-binary expression in for loop")
            print_line_marker_nowhitespace(lineno)


class ForClause(Node):

    def __init__(self, init, cond, post, lineno):
        super().__init__("FOR_CLAUSE", children=[init, cond, post])
        self.init = init
        self.cond = cond
        self.post = post
        self.lineno = lineno

        # signal the AST optimizer to not optimize these children
        self._no_optim = True

        if hasattr(cond, "type_") and getattr(cond, "type_") != "bool":
            print_error("Invalid condition", kind="TYPE ERROR")
            print("Cannot use non-binary expression in for loop")
            print_line_marker_nowhitespace(lineno)


class RangeClause(Node):

    def __init__(self, expr, ident_list=None, expr_list=None):
        if ident_list is not None:
            self.var_decl = make_variable_decls(ident_list, expr)
        else:
            self.var_decl = None
        super().__init__("RANGE",
                         children=[expr, ident_list, expr_list, self.var_decl])
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
                    self.fields.append(
                        StructField(ident.ident_name, i.type_, i.tag))
            elif i.embed_field is not None:
                # TODO: handle pointer type here
                self.fields.append(StructField(i.embed_field[1], None, i.tag))

        super().__init__("Struct", children=self.fields)


class StructField(Node):

    def __init__(self, name, type_, tag):
        self.f_name = name
        self.type_ = type_
        self.tag = tag

        super().__init__("StructField",
                         children=[type_],
                         data=(name, type_, tag))

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
    def __init__(self, typename: tuple, type_: Type, lineno: int):
        self.typename = typename
        self.type_ = type_

        super().__init__(name="TypeDef", children=[type_], data=typename)

        identifier: str = typename[1]
        symtab.add_if_not_exists(identifier)
        symtab.declare_new_variable(
                symbol=identifier,
                lineno=lineno,
                col_num=typename[2],
                type_=None,
                const=False,
                value=type_
            )


def get_typename(type_) -> str:
    """Returns just the typename from given type"""
    if isinstance(type_, str):
        return type_
    if isinstance(type_, Array) or isinstance(type_, Slice):
        return type_.typename
    if isinstance(type_, Struct):
        raise NotImplementedError("Type name for struct not supported yet")
    if isinstance(type_, List):
        raise NotImplementedError("Type name for List not supported yet")
    if isinstance(type_, Type):
        return str(type_.typename)

    raise Exception("Could not determine type from given:", type_)


def _optimize(node: Node) -> Node:
    num_list_childs = 0

    # a _no_optim attribute set to True signals this to not touch
    # the node's immediate children. Deeper children are optimized anyway.
    if not (hasattr(node, "_no_optim") and getattr(node, "_no_optim")):
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


def _postprocess(node: Node) -> Node:

    if isinstance(node, FunctionCall):
        if node.type_ is None:
            if node.fn_sym is not None:
                if node.fn_sym.value is not None:
                    node.type_ = node.fn_sym.value.signature.ret_type

    for i, child in enumerate(node.children):
        node.children[i] = _postprocess(child)

    return node


def postprocess_AST(ast: Node):
    ast = _postprocess(ast)
    return _optimize(ast)
