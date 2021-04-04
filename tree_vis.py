from typing import List
from collections import defaultdict
from syntree import Node
import syntree
import pydot


def get_node_name(node: Node, cache: defaultdict):
    return f"{node.name}_{cache[node.name]}"


def get_node_label(node: Node, cache: defaultdict):
    return f"{node.name}\n{node.data_str()}"


def _recur_draw(graph: pydot.Graph, cache: defaultdict, node: Node, rank: int = 0):
    # cache[node.name] += 1

    node_name = get_node_name(node, cache)
    # graph.add_node(pydot.Node(node_name, label=node_name, color="blue"))

    children: List[pydot.Node] = []

    for child in node.children:
        cache[child.name] += 1

        child_name = get_node_name(child, cache)
        child_label = get_node_label(child, cache)

        fillcolor = "turquoise"
        color = "red"

        if isinstance(child, syntree.List):
            fillcolor = "gray"
            color = "black"

        elif isinstance(child, syntree.IfStmt) or isinstance(child, syntree.ForStmt):
            fillcolor = "coral"
            color = "blue"

        elif isinstance(child, syntree.Identifier) or isinstance(
            child, syntree.QualifiedIdent
        ):
            fillcolor = "lightpink"
            color = "red"

        elif isinstance(child, syntree.Function):
            fillcolor = "palegreen"
            color = "blue"

        elif isinstance(child, syntree.Literal):
            fillcolor = "thistle"
            color = "purple"

        elif isinstance(child, syntree.BinOp) or isinstance(child, syntree.UnaryOp):
            fillcolor = "lightyellow"
            color = "orange"

        elif isinstance(child, syntree.Keyword):
            fillcolor = "lightblue"
            color = "navy"

        child_node = pydot.Node(
            child_name,
            label=child_label,
            group=node_name,
            fillcolor=fillcolor,
            color=color,
        )
        graph.add_node(child_node)
        children.append(child_node)

        graph.add_edge(pydot.Edge(node_name, child_name, weight=1.5))

        _recur_draw(graph, cache, child, rank + 1)

    # for child in node.children:

    # for child in node.children:
    # child_name = f"{child.name}_{cache[child.name]}"

    # graph.add_edge(pydot.Edge(

    # invis_nodes: List[pydot.Node] = []
    # for i in range(0, len(node.children) + 1):
    #     cache["invis"] += 1
    #     invis_node = pydot.Node(
    #         f"invis_{cache['invis']}", shape="point", width=0, height=0, rank=rank
    #     )

    #     graph.add_node(invis_node)

    #     invis_nodes.append(invis_node)

    # graph.add_edge(pydot.Edge(node_name, invis_nodes[0].get_name()))

    # for i in range(1, len(node.children)):
    #     child1 = invis_nodes[i]
    #     child2 = invis_nodes[i + 1]

    #     # child_name1 = f"{child1.get_name()}_{cache[child1.get_name()]}"
    #     # child_name2 = f"{child2.get_name()}_{cache[child2.get_name()]}"
    #     child_name1 = child1.get_name()
    #     child_name2 = child2.get_name()

    #     graph.add_edge(
    #         pydot.Edge(child_name1, child_name2, rank="same", style="invis", weight=100)
    #     )

    # for i, j in zip(children, invis_nodes[1:]):
    #     graph.add_edge(pydot.Edge(i.get_name(), j.get_name()))


def draw_AST(ast: Node):
    graph = pydot.Dot(
        "AST",
        graph_type="digraph",
        nodesep=1.0,
        ranksep=1.0,
        splines="ortho",
        overlap=False,
    )
    cache = defaultdict(lambda: 0)

    node_name = get_node_name(ast, cache)
    graph.add_node(pydot.Node(node_name, label=node_name))

    _recur_draw(graph, cache, ast)

    graph.write("ast.dot")

    return graph
