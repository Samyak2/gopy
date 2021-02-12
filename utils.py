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
        # print(str(self))

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


