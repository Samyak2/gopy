from math import log2
from copy import deepcopy

from tac import IntermediateCode, Quad, Assign, Operand, TempVar, ActualVar
from syntree import Literal


bools = {True: "true", False: "false"}


def is_power_of_2(x):
    return x and (not (x & (x - 1)))


def is_literal_or_const_operand(op):
    if isinstance(op, Literal):
        return True
    if isinstance(op, Operand) and op.is_const():
        return True
    return False


def binary_eval(q: Quad):
    dest, op1, operator, op2 = q.dest, q.op1, q.operator, q.op2

    if is_literal_or_const_operand(op1) and is_literal_or_const_operand(op2):
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
        q = Assign(dest, dest.value)
    elif is_literal_or_const_operand(op1) and isinstance(op2, Operand):
        if is_power_of_2(op1.value) and operator == "*":
            q.op1, q.op2 = q.op2, int(log2(op1.value))
            q.operator = "<<"
        elif op1.value == 0:
            if operator == "+":
                q = Assign(dest, op2)
            elif operator == "*":
                q = Assign(dest, 0)
            elif operator == "/":
                q = Assign(dest, 0)
        elif op1.value == 1 and operator == "*":
            q = Assign(dest, op2)
        elif op1.value == "true" and operator == "&&":
            q = Assign(dest, op2)
        elif op1.value == "false" and operator == "||":
            q = Assign(dest, op2)
    elif is_literal_or_const_operand(op2) and isinstance(op1, Operand):
        if is_power_of_2(op2.value):
            q.op2 = int(log2(op2.value))
            if operator == "*":
                q.operator = "<<"
            elif operator == "/":
                q.operator = ">>"
        elif op2.value == 0:
            if operator == "+":
                q = Assign(dest, op1)
            elif operator == "*":
                q = Assign(dest, 0)
            elif operator == "/":
                q = Assign(dest, 0)
        elif op2.value == 1 and operator == "*":
            q = Assign(dest, op1)
        elif op2.value == "true" and operator == "&&":
            q = Assign(dest, op1)
        elif op2.value == "false" and operator == "||":
            q = Assign(dest, op1)
    else:
        pass
    return q


def remove_unused_temps(ic):
    required_temps = set()
    ico = IntermediateCode()

    for q in reversed(ic.code_list):
        if isinstance(q.dest, TempVar):
            if q.operator == "call":
                pass
            elif not (q.dest in required_temps):
                continue
        ico.add_to_list(q)
        if isinstance(q.op1, TempVar):
            required_temps.add(q.op1)
        if isinstance(q.op2, TempVar):
            required_temps.add(q.op2)

    ico.code_list = ico.code_list[::-1]

    return ico


def remove_deadcode(ic):
    required_ops = set()
    ico = IntermediateCode()

    for q in reversed(ic.code_list):
        if q.operator == "return":
            required_ops = set()
            required_ops.add(q.op2)
            ico = IntermediateCode()
            ico.add_to_list(q)
        elif q.dest in required_ops:
            ico.add_to_list(q)
            if isinstance(q.op1, Operand):
                required_ops.add(q.op1)
            if isinstance(q.op2, Operand):
                required_ops.add(q.op2)

    ico.code_list = ico.code_list[::-1]

    # ico = IntermediateCode()
    # for q in ic.code_list:
    #     if q.operator == 'return':
    #         ico = IntermediateCode()
    #         ico.add_to_list(q)
    #     elif q.dest in required_ops:
    #         ico.add_to_list(q)

    return ico


def copy_prop(ic):
    copy_prop_vars = {}
    ico = IntermediateCode()

    for q in ic.code_list:
        if isinstance(q, Assign):
            if isinstance(q.dest, ActualVar):
                if isinstance(q.op2, ActualVar) and not q.op2.is_const():
                    copy_prop_vars[q.dest] = q.op2
                    continue
        if q.op1 in copy_prop_vars:
            q.op1 = copy_prop_vars[q.op1]
        if q.op2 in copy_prop_vars:
            q.op2 = copy_prop_vars[q.op2]
        ico.add_to_list(q)

    return ico


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

    for q in ic.code_list:

        # print("before optimization:")
        # print_quad_info(q)

        if isinstance(q, Assign):
            if isinstance(q.op2, Literal):
                q.dest.value = q.op2.value
            elif isinstance(q.op2, Operand) and q.op2.is_const():
                q.dest.value = q.op2.value
                q.op2 = q.dest.value

        q = binary_eval(q)

        # print("after optimization:")
        # print_quad_info(q)

        ico.add_to_list(q)

    print("After Constant Folding, Constant Propagation and Strength Reduction:")
    print(ico)
    print("The above table is before removing unused temps")
    print()

    ico = remove_unused_temps(ico)

    print("After removing unsued temps:")
    print(ico)
    print("The above table is before performing Copy Propagation")
    print()

    ico = copy_prop(ico)

    print("Final Optimized Intermediate Code after Copy Propogation:")
    print(ico)
    print()

    # print("Before removing dead code:")
    # print(ico)

    # ico = remove_deadcode(ico)

    # print("After removing dead code:")

    return ico
