class Node:
    """Node of an AST"""

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

    @property
    def left(self):
        return self.children[0]

    @property
    def right(self):
        return self.children[1]


class Assignment(BinOp):
    """Node for assignment operations"""


class UnaryOp(Node):
    """Node for unary operations"""

    def __init__(self, operator, operand):
        if isinstance(operand, UnaryOp) and operand.operator is None:
            operand = operand.operand
        super().__init__(f"Unary {operator}", children=[operand], data=operator)

    @property
    def operator(self):
        return self.data

    @property
    def operand(self):
        return self.children[0]


class PrimaryExpr(Node):
    """Node for PrimaryExpr

    Ref: https://golang.org/ref/spec#PrimaryExpr
    """

    def __init__(self, operand):
        super().__init__("PrimaryExpr", children=[], data=operand)


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


class Signature(Node):
    """Node to store function signature"""

    def __init__(self, parameters, result=None):
        super().__init__("signature", children=[parameters, result])

    @property
    def parameters(self):
        return self.children[0]

    @property
    def result(self):
        return self.children[1]


class Function(Node):
    """Node to store function declaration"""

    def __init__(self, name, signature, body=None):
        super().__init__("FUNCTION", children=[signature, body], data=name)
        self.fn_name = name

    @property
    def signature(self):
        return self.children[0]

    @property
    def body(self):
        if len(self.children) > 1:
            return self.children[1]
        else:
            return None


class Type(Node):
    """Parent class for all types"""


class Array(Type):
    """Node for an array type"""

    def __init__(self, eltype, length):
        super().__init__("ARRAY", children=[length], data=eltype)
        self.eltype = eltype

    @property
    def length(self):
        return self.children[0]


class Identifier(Node):
    """Node for identifiers"""

    def __init__(self, ident_tuple):
        super().__init__("IDENTIFIER", children=[], data=ident_tuple[1])


class QualifiedIdent(Node):
    """Node for qualified identifiers"""

    def __init__(self, package_name, identifier):
        super().__init__("IDENTIFIER", children=[], data=(package_name, identifier))


class VariableDecl(Node):
    """Node to store variable and constant declarations"""

    def __init__(self, identifier_list, type_=None, expression_list=None, const=False):
        super().__init__(
            "DECL",
            children=[identifier_list, expression_list],
            data=(type_, const),
        )

    @property
    def expression_list(self):
        return self.children[1]

    @property
    def identifier_list(self):
        return self.children[0]

    @property
    def type_(self):
        return self.data[0]

    @property
    def is_const(self):
        return self.data[1]


# class OldNode:
#     """Class to store a node of the AST"""

#     def __init__(self, type_, children=None, node=None):
#         self.type = type_
#         if children is not None:
#             new_children = []
#             for child in children:
#                 if child is None:
#                     continue

#                 if not isinstance(child, Node):
#                     new_children.append(Node(type(child), node=child))
#                 else:
#                     new_children.append(child)
#             self.children = new_children
#         else:
#             self.children = []
#         self.node = node
#         # print(str(self))

#     def __str__(self):
#         return f"<{self.type}, {self.node}>"

#     def __repr__(self):
#         return f"<Node: {self.type}, {self.node}, {self.children}>"

#     @staticmethod
#     def print_node(child):
#         if isinstance(child, Node):
#             print(f"{child.type}: {child.node}")
#         elif isinstance(child, lex.LexToken):
#             print(f"{child.type}: {child.value}")
#         else:
#             print(f"{child}")

#     def print_level_order(self):

#         queue = []

#         queue.append(self)

#         while queue:

#             node = queue.pop(0)
#             Node.print_node(node)

#             if isinstance(node, Node):
#                 queue.extend(node.children)

#     def add_child(self, child):
#         if child is not None:
#             if not isinstance(child, Node):
#                 self.children.append(Node(type(child), node=child))
#             else:
#                 self.children.append(child)
