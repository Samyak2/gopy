class Node:
    """Node of an AST"""

    def __init__(self, name, **kwargs):
        self.name = name
        self.children: list = [c for c in kwargs["children"] if c is not None]
        self.data = kwargs.get("data", None)

    def __repr__(self):
        return f"<Node: {self.name}; {self.data}; {self.children}>"

    def __str__(self):
        return f"<Node: {self.name}; {self.data}; {len(self.children)} child(s)>"

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
        super().__init__(f"Unary {operator}", children=[operand], data=operator)

    @property
    def operator(self):
        return self.data

    @property
    def operand(self):
        return self.children[0]


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


class Function(Node):
    """Node to store function declaration"""

    def __init__(self, name, signature, body=None):
        super().__init__("FUNCTION", children=[signature, body], data=name)
        self.name = name

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
    "Parent class for all types"""


class Array(Type):
    """Node for an array type"""

    def __init__(self, eltype, length):
        super().__init__("ARRAY", children=[length], data=eltype)
        self.eltype = eltype

    @property
    def length(self):
        return self.children[0]

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


