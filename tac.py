from typing import List

from tabulate import tabulate

import syntree


class Quad:
    dest = None
    op1 = None
    op2 = None
    operator = None

    def __init__(self, dest, op1, op2, operator):
        self.dest = dest
        self.op1 = op1
        self.op2 = op2
        self.operator = operator

    def print_info(self):
        print("{} = {} {} {}".format(self.dest, self.op1, self.operator, self.op2))


class IntermediateCode:
    def __init__(self):
        self.code_list: List[Quad] = []
        self.temp_var_count = 0

    def get_new_temp_var(self):
        self.temp_var_count += 1
        return "t" + str(self.temp_var_count)

    def add_to_list(self, code: Quad):
        self.code_list.append(code)

    def print_three_address_code(self):
        for i in self.code_list:
            print("{} = {} {} {}".format(i.dest, i.op1, i.operator, i.op2))

    def __str__(self) -> str:
        return str(
            tabulate(
                [[i.dest, i.op1, i.operator, i.op2] for i in self.code_list],
                headers=["Dest", "Operand 1", "Operator", "Operand 2"],
                tablefmt="psql",
            )
        )


def _recur_codegen(node: syntree.Node, ic: IntermediateCode):
    # process all child nodes before parent
    # ast is from right to left, so need to traverse in reverse order

    new_children = []
    for child in reversed(node.children):
        new_children.append(_recur_codegen(child, ic))

    new_children.reverse()

    return_val = []

    if isinstance(node, syntree.BinOp):
        temp = ic.get_new_temp_var()

        # the children can be temporaries made in the _recur_codegen call above
        # so they are stored in new_children which is used here
        # each return value is a list, so the second [0] is needed
        ic.add_to_list(
            Quad(temp, new_children[0][0], new_children[1][0], node.operator)
        )

        return_val.append(temp)

    elif isinstance(node, syntree.Literal):
        temp = ic.get_new_temp_var()

        # TODO: how to handle type here?
        ic.add_to_list(Quad(temp, None, node.value, "="))

        return_val.append(temp)

    # elif isinstance(node, syntree.Identifier):

    #     return_val.append(node.ident_name)

    elif isinstance(node, syntree.PrimaryExpr):

        if isinstance(node.data, tuple) and node.data[0] == "identifier":
            return_val.append(node.data[1])

        elif (
            node.data is None
            and len(new_children) == 2
            and isinstance(new_children[1][0], syntree.Index)
        ):
            # TODO: do array/slice indexing here
            return_val.append(node)
            pass
            # temp1 = ic.get_new_temp_var()

        # TODO: implement other variants of PrimaryExpr

        else:
            return_val.append(node)

    # TODO: implement other AST nodes too

    else:
        print(f"Intermediate code is not yet implemented for node {node}")

        return_val.append(node)

    return return_val


def intermediate_codegen(ast: syntree.Node) -> IntermediateCode:
    ic = IntermediateCode()

    _recur_codegen(ast, ic)

    return ic
