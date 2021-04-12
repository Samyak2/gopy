from symbol_table import SymbolInfo
from typing import Any, List, Optional

from tabulate import tabulate

import syntree
from go_lexer import symtab, type_table


class Quad:
    dest = None
    op1 = None
    op2 = None
    operator = None

    #  func_name = None

    def __init__(self, dest, op1, op2, operator):
        self.dest = dest
        self.op1 = op1
        self.op2 = op2
        self.operator = operator
        #  self.func_name = str(func_name)

    def print_info(self):
        print(str(self))

    def __str__(self):
        return "{} = {} {} {}".format(self.dest, self.op1, self.operator, self.op2)


class TempVar:
    def __init__(self, id):
        self.name = "t" + str(id)
        self.const_flag = False
        self.value = None

    def is_const(self):
        return self.const_flag

    def make_const(self, value):
        self.const_flag = True
        self.value = value

    def __str__(self):
        return self.name


class IntermediateCode:
    def __init__(self):
        #  self.code_list: List[Quad] = {Quad.func_name: []}
        self.code_list: List[Quad] = []
        self.temp_var_count = 0

    def get_new_temp_var(self):
        self.temp_var_count += 1
        return TempVar(self.temp_var_count)
        # return "t" + str(self.temp_var_count)

    def add_to_list(self, code: Quad):
        self.code_list.append(code)
        #  self.code_list[Quad.func_name].append(code)

    def print_three_address_code(self):
        for i in self.code_list:
            print("{} = {} {} {}".format(i.dest, i.op1, i.operator, i.op2))
        #  for i in self.code_list:
        #      print("{} : ".format(i))
        #      for j in range(len(self.code_list[i])):
        #          print("%5d:\t" % j, self.code_list[i][j])

    def __str__(self) -> str:
        return str(
            tabulate(
                [[i.dest, i.op1, i.operator, i.op2] for i in self.code_list],
                headers=["Dest", "Operand 1", "Operator", "Operand 2"],
                tablefmt="psql",
            )
        )


def tac_BinOp(
    ic: IntermediateCode,
    node: syntree.BinOp,
    new_children: List[List[Any]],
    return_val: List[Any],
):
    temp = ic.get_new_temp_var()

    # the children can be temporaries made in the _recur_codegen call above
    # so they are stored in new_children which is used here
    # each return value is a list, so the second [0] is needed
    ic.add_to_list(Quad(temp, new_children[0][0], new_children[1][0], node.operator))

    return_val.append(temp)


def tac_Literal(
    ic: IntermediateCode,
    node: syntree.Literal,
    new_children: List[List[Any]],
    return_val: List[Any],
):
    temp = ic.get_new_temp_var()
    temp.make_const(node.value)

    # TODO: how to handle type here?
    ic.add_to_list(Quad(temp, None, node.value, "="))

    return_val.append(temp)


def tac_PrimaryExpr(
    ic: IntermediateCode,
    node: syntree.PrimaryExpr,
    new_children: List[List[Any]],
    return_val: List[Any],
):
    if isinstance(node.data, tuple) and node.data[0] == "identifier":
        # a simple identifier
        if not node.children:
            return_val.append(node.data[1])

        # not so simple identifier
        elif len(node.children) == 1 and isinstance(node.children[0], syntree.Index):
            arr_name = node.data[1]
            index: syntree.Index = node.children[0]
            ident: Optional[SymbolInfo] = node.ident

            base_addr_t = ic.get_new_temp_var()
            ic.add_to_list(Quad(base_addr_t, None, f"base({arr_name})", "="))
            # return_val.append(base_addr_t)

            if ident is not None:
                ind = new_children[0][0][0]
                width = type_table.get_type(ident.type_.eltype).storage

                offset_t = ic.get_new_temp_var()
                ic.add_to_list(Quad(offset_t, ind, width, "*"))

                index_t = ic.get_new_temp_var()
                ic.add_to_list(Quad(index_t, base_addr_t, offset_t, "+"))

                res_t = ic.get_new_temp_var()
                ic.add_to_list(Quad(res_t, arr_name, index_t, "[]"))

                return_val.append(res_t)
            else:
                print("uhhh could not get type")

                return_val.append(node)

        else:

            return_val.append(node)

    elif (
        node.data is None
        and len(new_children) == 2
        and isinstance(new_children[1][0], syntree.Index)
    ):
        # TODO: do array/slice indexing here
        print("array/slice indexing: ", new_children)
        arr_name_, index_ = new_children
        arr_name = arr_name_[0]
        index: syntree.Index = index_[0]
        ident: Optional[SymbolInfo] = node.ident

        # temp1 = ic.get_new_temp_var()
        base_addr_t = ic.get_new_temp_var()
        ic.add_to_list(Quad(base_addr_t, None, f"base({arr_name})", "="))
        return_val.append(base_addr_t)

        if ident is not None:
            print(ident.type_)
        else:
            print("This should not be None, something is wrong", index, arr_name)

    # TODO: implement other variants of PrimaryExpr

    else:
        return_val.append(node)


def tac_Index(
    ic: IntermediateCode,
    node: syntree.Index,
    new_children: List[List[Any]],
    return_val: List[Any],
):
    return_val.append(new_children[0])


# def tac_Array(
#     ic: IntermediateCode,
#     node: syntree.Array,
#     new_children: List[List[Any]],
#     return_val: List[Any],
# ):
#     temp = ic.get_new_temp_var()

#     ic.add_to_list(Quad(temp, None,

new_scope_nodes = {"Function", "IfStmt", "ForStmt"}


def _recur_codegen(node: syntree.Node, ic: IntermediateCode):
    # process all child nodes before parent
    # ast is from right to left, so need to traverse in reverse order

    node_class_name = node.__class__.__name__

    new_children = []
    for child in reversed(node.children):
        new_children.append(_recur_codegen(child, ic))

    new_children.reverse()

    return_val = []

    tac_fn_name = f"tac_{node_class_name}"

    if tac_fn_name in globals():
        globals()[tac_fn_name](ic, node, new_children, return_val)

    # elif isinstance(node, syntree.Identifier):

    #     return_val.append(node.ident_name)

    # TODO: implement other AST nodes too

    else:
        print(f"Intermediate code is not yet implemented for node {node}")

        return_val.append(node)

    return return_val


def intermediate_codegen(ast: syntree.Node) -> IntermediateCode:
    ic = IntermediateCode()

    _recur_codegen(ast, ic)

    return ic
