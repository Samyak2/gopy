from copy import deepcopy
from tac import IntermediateCode, Quad, Assign, Operand

def optimize_ic(ic):
    ic = deepcopy(ic)
    ico = IntermediateCode()

    for i, q in enumerate(ic.code_list):
        if isinstance(q.op2, Operand):
            # print("before optimization:")
            # print(q)
            # print(q.dest, type(q.dest))
            # print(q.op1, type(q.op1))
            # if isinstance(q.op1, Operand): print(q.op1.is_const())
            # print(q.operator, type(q.operator))
            # print(q.op2, type(q.op2))
            # if isinstance(q.op2, Operand): print(q.op2.is_const())
            # print()
            if isinstance(q, Assign) and q.op2.is_const():
                q.dest.value = q.op2.value
                q.op2 = q.dest.value
            elif isinstance(q.op1, Operand) and q.op1.is_const() and q.op2.is_const():
                if q.operator == '+':
                    q.dest.value = q.op1.value + q.op2.value
                elif q.operator == '-':
                    q.dest.value = q.op1.value - q.op2.value
                elif q.operator == '*':
                    q.dest.value = q.op1.value * q.op2.value
                elif q.operator == '/':
                    q.dest.value = q.op1.value / q.op2.value
                q = Assign(q.dest, q.dest.value)
            # print("after optimization:")
            # print(q)
            # print(q.dest, type(q.dest))
            # print(q.op1, type(q.op1))
            # print(q.operator, type(q.operator))
            # print(q.op2, type(q.op2))
            # print()
        ico.add_to_list(q)

    return ico
