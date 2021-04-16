from math import log2, floor, ceil

from tac import IntermediateCode, Label, Quad, Assign, Operand, TempVar, ActualVar
from syntree import Literal


bools = {True: "true", False: "false"}


def is_power_of_2(x):
    if floor(x) != ceil(x) or x == 1:
        return False
    x = int(x)
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
            ints = {"int", "int8", "int16", "int32", "int64"}
            floats = {"float32", "float64"}
            if dest.type_ in ints:
                dest.value = op1.value // op2.value
            elif dest.type_ in floats:
                dest.value = op1.value / op2.value
            else:
                # raise NotImplementedError(
                #     "Support for types other than int and float have not been added yet!"
                # )
                pass

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
        q = Assign(dest, dest.value, q.scope_id)
    elif is_literal_or_const_operand(op1) and isinstance(op2, Operand):
        if is_power_of_2(op1.value) and operator == "*":
            q.op1, q.op2 = q.op2, int(log2(op1.value))
            q.operator = "<<"
        elif op1.value == 0:
            if operator == "+":
                q = Assign(dest, op2, q.scope_id)
            elif operator == "*":
                q = Assign(dest, 0, q.scope_id)
            elif operator == "/":
                q = Assign(dest, 0, q.scope_id)
        elif op1.value == 1 and operator == "*":
            q = Assign(dest, op2, q.scope_id)
        elif op1.value == "true" and operator == "&&":
            q = Assign(dest, op2, q.scope_id)
        elif op1.value == "false" and operator == "||":
            q = Assign(dest, op2, q.scope_id)
    elif is_literal_or_const_operand(op2) and isinstance(op1, Operand):
        if is_power_of_2(op2.value):
            q.op2 = int(log2(op2.value))
            if operator == "*":
                q.operator = "<<"
            elif operator == "/":
                q.operator = ">>"
        elif op2.value == 0:
            if operator == "+":
                q = Assign(dest, op1, q.scope_id)
            elif operator == "*":
                q = Assign(dest, 0, q.scope_id)
            elif operator == "/":
                q = Assign(dest, 0, q.scope_id)
        elif op2.value == 1 and operator == "*":
            q = Assign(dest, op1, q.scope_id)
        elif op2.value == "true" and operator == "&&":
            q = Assign(dest, op1, q.scope_id)
        elif op2.value == "false" and operator == "||":
            q = Assign(dest, op1, q.scope_id)
    else:
        pass
    return q


def loop_invariant(ic: IntermediateCode):
    loops = {}

    for i, code in enumerate(ic.code_list):
        if isinstance(code, Label):
            if code.name.startswith("for_simple_start") or code.name.startswith(
                "for_cmpd_start"
            ):
                loops[code.name] = (i,)

            elif code.name.startswith("for_simple_end") or code.name.startswith(
                "for_cmpd_end"
            ):
                start_name = code.name.replace("end", "start")
                loops[start_name] = (loops[start_name][0], i)

    print("got loops", loops)

    def _loop_invar(ic: IntermediateCode, loop_start: int, loop_end: int):
        required = {}
        blacklisted = set()

        def _is_literal_const_or_required(op: Quad):
            return (
                is_literal_or_const_operand(op) or op in required
            ) and op not in blacklisted

        for ind, code in enumerate(ic.code_list[loop_start:loop_end]):

            if isinstance(code, Assign) or isinstance(code.dest, (ActualVar, TempVar)):
                flag = False

                if code.op1 is None:
                    if _is_literal_const_or_required(code.op2):
                        required[code.dest] = (ind, code, [code.op2])
                        flag = True

                else:
                    if _is_literal_const_or_required(
                        code.op1
                    ) and _is_literal_const_or_required(code.op2):
                        required[code.dest] = (ind, code, [code.op1, code.op2])
                        flag = True

                if not flag:
                    if code.dest in required:
                        print("is dest, removing", code.dest)
                        required.pop(code.dest)
                        blacklisted.add(code.dest)

        print("required in loop", required.keys())

        codes = []
        moved = set()
        for ind, code, dep_list in reversed(required.values()):
            flag = True
            for dep in dep_list:
                if not _is_literal_const_or_required(dep):
                    flag = False

            if not flag:
                continue

            new_ind = loop_start + ind

            codes.append((ic.code_list.pop(new_ind), dep_list))
            moved.add(codes[-1][0].dest)

        for code_, dep_list in codes:
            flag = True
            for dep in dep_list:
                if dep in required and dep not in moved:
                    flag = False

            if not flag:
                continue

            print("moving to", loop_start, ic.code_list[loop_start])

            ic.code_list.insert(loop_start, code_)

    for _, (start, end) in loops.items():
        _loop_invar(ic, start, end)


def pack_temps(ic):
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

    modified_temp_var_count = 0
    modified_temp_vars = set()

    for q in ico.code_list:
        # print_quad_info(q)
        for op in (q.op1, q.op2, q.dest):
            if isinstance(op, TempVar):
                temp = op
                if temp in modified_temp_vars:
                    continue
                modified_temp_var_count += 1
                temp.name = modified_temp_var_count
                modified_temp_vars.add(temp)

    return ico


def remove_deadcode(ic):
    ico1 = IntermediateCode()

    curr_scope = "0"
    discard = False
    for q in ic.code_list:
        if discard:
            if q.operator == "LABEL":
                ico1.add_to_list(q)
            elif q.scope_id == curr_scope:
                continue
            else:
                discard = False
                ico1.add_to_list(q)
        else:
            ico1.add_to_list(q)
        if q.operator == "return":
            discard = True
            curr_scope = q.scope_id

    ico2 = IntermediateCode()

    required_ops = set()

    for q in reversed(ico1.code_list):
        if q.operator == "LABEL":
            ico2.add_to_list(q)
            required_ops.add(q.dest)
        elif q.operator == "call":
            ico2.add_to_list(q)
            required_ops.add(q.dest)
        elif q.operator in ("return", "push"):
            ico2.add_to_list(q)
            required_ops.add(q.op2)
        elif q.dest in required_ops:
            ico2.add_to_list(q)
            if isinstance(q.op1, Operand):
                required_ops.add(q.op1)
            if isinstance(q.op2, Operand):
                required_ops.add(q.op2)

    ico2.code_list = ico2.code_list[::-1]

    return ico2


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


# def common_subexpression_elimination(ic):


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
    loop_invariant(ic)

    print("Intermediate Code after loop invariant")
    print(ic)

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
    # print("The above table is before removing unused temps")
    # print()

    # ico = pack_temps(ico)

    # print("After removing unsued temps:")
    # print(ico)
    print("The above table is before performing Copy Propagation")
    print()

    ico = copy_prop(ico)

    print("After Copy Propogation:")
    print(ico)
    # print("The above table is before performing Common Subexpression Elimination")
    # print()

    # ico = common_subexpression_elimination(ico)

    # print("Final Optimized Intermediate Code after Common Subexpression Elimination:")
    # print(ico)

    # print("Before removing dead code:")
    # print(ico)

    ico = remove_deadcode(ico)

    print("After removing dead code:")
    print(ico)

    return ico
