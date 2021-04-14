from copy import deepcopy
from tac import IntermediateCode, Quad, Assign, Operand


bools = {True: 'true', False: 'false'}


def binary_eval(dest: Quad, op1: Quad, operator: str, op2: Quad):
    op1, op2 = op1.value, op2.value
    if operator == '+':
        dest.value = op1 + op2
    elif operator == '-':
        dest.value = op1 - op2
    elif operator == '*':
        dest.value = op1 * op2
    elif operator == '/':
        # TODO: calculate result based on type of dest
        # ints = {'int', 'int8', 'int16', 'int32', 'int64'}
        # floats = {'float32', 'float64'}
        # if dest.symbol.type_.name in ints:
        #     dest.value = op1 // op2
        # elif dest.symbol.type_.name in floats:
        #     dest.value = op1 / op2
        # else:
        #     raise NotImplementedError("Support for types other than int and float have not been added yet!")
        
        dest.value = op1 / op2
    elif operator == '==':
        dest.value = bools[op1 == op2]
    elif operator == '!=':
        dest.value = bools[op1 != op2]
    elif operator == '<':
        dest.value = bools[op1 < op2]
    elif operator == '>':
        dest.value = bools[op1 > op2]
    elif operator == '<=':
        dest.value = bools[op1 <= op2]
    elif operator == '>=':
        dest.value = bools[op1 >= op2]
    else:
        raise Exception(operator + " is an invalid binary operator!")


def print_quad_info(q: Quad):
    print('Quad (q):', q)
    print('type of q:', type(q))
    print('type of q.dest:', type(q.dest), '; const_flag: ' + str(q.dest.is_const()) if isinstance(q.dest, Operand) else '')
    print('type of q.op1:', type(q.op1), '; const_flag: ' + str(q.op1.is_const()) if isinstance(q.op1, Operand) else '')
    print('type of q.op2:', type(q.op2), '; const_flag: ' + str(q.op2.is_const()) if isinstance(q.op2, Operand) else '')
    print()


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
            elif isinstance(q.op1, Operand) and q.op1.is_const() and q.op2.is_const():
                binary_eval(q.dest, q.op1, q.operator, q.op2)
                q = Assign(q.dest, q.dest.value)
        
        print("after optimization:")
        print_quad_info(q)
        
        ico.add_to_list(q)

    return ico
