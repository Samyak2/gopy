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

    def data_str(self) -> str:
        return "" if self.data is None else str(self.data)

    def add_child(self, child):
        if child is not None:
            self.children.append(child)


class BinOp(Node):
    """Node for binary operations"""

    def __init__(self, operator, left=None, right=None, type_=None):
        super().__init__("Binary", children=[left, right], data=operator)
        self.operator = self.data
        self.left = left
        self.right = right

        ###############
        # Starts Here #
        ###############
        self.type_ = None
        x = self.children[0].data[0]  # left operand
        y = self.children[1].data[0]  # right operand

        def check_type(x, y):
           if x == 'int':
               if y == "float64":
                   self.type_ = "float64"

               elif y == 'bool':
                   self.type_ = "int"
               return 1

           elif x == "float64":
               if y == "bool":
                   self.type_ = "float64"
                   return 1

           #  elif y == str or y == bool or y == complex:
           return 0

        if x != y:
           val1 = check_type(x, y)
           val2 = check_type(y, x)
           if not (val1 | val2):
               print("Error: Type Mismatch")
        else:
           self.type_ = x
        #############
        # Ends here #
        #############


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


class PrimaryExpr(Node):
    """Node for PrimaryExpr

    Ref: https://golang.org/ref/spec#PrimaryExpr
    """

    def __init__(self, operand, children=None):
        super().__init__("PrimaryExpr",
                         children=[] if children is None else children,
                         data=operand)

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


class Signature(Node):
    """Node to store function signature"""

    def __init__(self, parameters, result=None):
        super().__init__("signature", children=[parameters, result])
        self.parameters = parameters
        self.result = result


class Function(Node):
    """Node to store function declaration"""

    def __init__(self, name, signature, lineno: int, body=None):
        super().__init__("FUNCTION",
                         children=[signature, body],
                         data=(name, lineno))
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
        self.eltype = eltype
        self.length = length

    def data_str(self):
        return f"eltype: {self.eltype}"


class Slice(Type):
    """Node for a slice type"""

    def __init__(self, eltype):
        super().__init__("SLICE", children=[], data=eltype)
        self.eltype = eltype

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


class QualifiedIdent(Node):
    """Node for qualified identifiers"""

    def __init__(self, package_name, identifier):
        super().__init__("IDENTIFIER",
                         children=[],
                         data=(package_name, identifier))

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

        children = []

        if isinstance(type_, Node):
            children.append(type_)

        if isinstance(value, Node):
            children.append(value)

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
        for ident, expr in zip(identifier_list, expression_list):
            # TODO: check value is appropriate for type

            ###############################
            # From here the changes start #
            ###############################

            #  expr -> right side
            #  type -> left side

            if expr == None:
                print("Error: Variable not defined earlier")
                return

            if (expr and type_ != None and type_ != "string" and
                    type_.data != expr.data[0]):
                #  print(type_.data, expr)
                if (type_.data == "float64" and
                        expr.data[0] == "int") or (type_.data == "int" and
                                                   expr.data[0] == "float64"):
                    type_.data = expr.data[0]
                else:
                    print("Error: mismatch in VarDecl types")
                    return

            else:
                if not type_:
                    type_ = expr.data[0]
            #  print("type is: ", type_)
            #  print("value is:", expr)  # right side

            ################
            #  Ends here
            ################

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
            self.var_decl = make_variable_decls(ident_list)

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

    def __init__(self, typename, type_: Type, type_table, lineno):
        self.typename = typename
        self.type_ = type_

        super().__init__(name="TypeDef", children=[type_], data=typename)

        type_table.add_type(typename[1], lineno, typename[2], None)


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
