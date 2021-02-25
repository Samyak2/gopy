from pptree.utils import *
from pptree.pptree import print_tree_horizontally, print_tree_vertically


def print_tree(current_node, childattr='children', nameattr='name', horizontal=True):
    if nameattr is None:
        name = lambda node: str(node)
    elif hasattr(current_node, nameattr):
        name = lambda node: getattr(node, nameattr)
    else:
        name = lambda node: str(node)

    children = lambda node: getattr(node, childattr)
    nb_children = lambda node: sum(nb_children(child) for child in children(node)) + 1

    def balanced_branches(current_node):
        size_branch = {child: nb_children(child) for child in children(current_node)}

        """ Creation of balanced lists for "a" branch and "b" branch. """
        a = children(current_node)
        b = []
        while a and sum(size_branch[node] for node in b) < sum(size_branch[node] for node in a):
            b.insert(0, a.pop())

        return a, b

    if horizontal:
        print_tree_horizontally(current_node, balanced_branches, name)

    else:
        print_tree_vertically(current_node, balanced_branches, name, children)
