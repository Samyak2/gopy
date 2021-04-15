from math import log2
from copy import deepcopy

from tac import IntermediateCode, Quad, Assign, Operand


bools = {True: "true", False: "false"}


def is_power_of_2(x):
    return x and (not (x & (x - 1)))


def binary_eval(q: Quad):
    dest, op1, operator, op2 = q.dest, q.op1, q.operator, q.op2

    if op1.is_const() and op2.is_const():
        if operator == "+":
            dest.value = op1.value + op2.value
        elif operator == "-":
            dest.value = op1.value - op2.value
        elif operator == "*":
            dest.value = op1.value * op2.value
        elif operator == "/":
            # TODO: calculate result based on type of dest
            # ints = {'int', 'int8', 'int16', 'int32', 'int64'}
            # floats = {'float32', 'float64'}
            # if dest.symbol.type_.name in ints:
            #     dest.value = op1.value // op2.value
            # elif dest.symbol.type_.name in floats:
            #     dest.value = op1.value / op2.value
            # else:
            #     raise NotImplementedError("Support for types other than int and float have not been added yet!")

            dest.value = op1.value / op2.value
        elif operator == "==":
            dest.value = bools[op1.value == op2.value]
        elif operator == "!=":
            dest.value = bools[op1.value != op2.value]
        elif operator == "<":
            dest.value = bools[op1.value < op2.value]
        elif operator == ">":
            dest.value = bools[op1.value > op2.value]
        elif operator == "<=":
            dest.value = bools[op1.value <= op2.value]
        elif operator == ">=":
            dest.value = bools[op1.value >= op2.value]
        else:
            raise Exception(operator + " is an invalid binary operator!")
        q = Assign(q.dest, q.dest.value)
    elif op1.is_const():
        if is_power_of_2(op1.value) and operator == "*":
            q.op1, q.op2 = q.op2, int(log2(op1.value))
            q.operator = "<<"
    elif q.op2.is_const():
        if is_power_of_2(op2.value):
            q.op2 = int(log2(op2.value))
            if operator == "*":
                q.operator = "<<"
            elif operator == "/":
                q.operator = ">>"
    else:
        pass
    return q


def print_quad_info(q: Quad):
    print("Quad (q):", q)
    print("type of q:", type(q))
    print(
        "type of q.dest:",
        type(q.dest),
        "; const_flag: " + str(q.dest.is_const())
        if isinstance(q.dest, Operand)
        else "",
    )
    print(
        "type of q.op1:",
        type(q.op1),
        "; const_flag: " + str(q.op1.is_const()) if isinstance(q.op1, Operand) else "",
    )
    print(
        "type of q.op2:",
        type(q.op2),
        "; const_flag: " + str(q.op2.is_const()) if isinstance(q.op2, Operand) else "",
    )
    print()


# NOTE: Original ic is modified during optimization
def optimize_ic(ic):
    ic = deepcopy(ic)
    ico = IntermediateCode()

    for i, q in enumerate(ic.code_list):

        print("before optimization:")
        print_quad_info(q)

        if isinstance(q.op2, Operand):
            if isinstance(q, Assign) and q.op2.is_const():
                q.dest.value = q.op2.value
                q.op2 = q.dest.value
            elif isinstance(q.op1, Operand):
                q = binary_eval(q)

        print("after optimization:")
        print_quad_info(q)

        ico.add_to_list(q)

    return ico
