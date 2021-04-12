import tac

def optimize_ic(ic):
    for i, q in enumerate(ic.code_list):
        # print("before optimization:")
        # print(q)
        # print(q.dest, type(q.dest))
        # print(q.op1, type(q.op1))
        # print(q.operator, type(q.operator))
        # print(q.op2, type(q.op2))
        if isinstance(q.op1, tac.TempVar) and isinstance(q.op2, tac.TempVar):
            if q.op1.is_const() and q.op2.is_const():
                if q.operator == '+':
                    q.dest.make_const(q.op1.value + q.op2.value)
                elif q.operator == '-':
                    q.dest.make_const(q.op1.value - q.op2.value)
                elif q.operator == '*':
                    q.dest.make_const(q.op1.value * q.op2.value)
                elif q.operator == '/':
                    q.dest.make_const(q.op1.value / q.op2.value)
                q.op1 = None
                q.operator = '='
                q.op2 = q.dest.value
        # print("after optimization:")
        # print(q)
        # print(q.dest, type(q.dest))
        # print(q.op1, type(q.op1))
        # print(q.operator, type(q.operator))
        # print(q.op2, type(q.op2))

    return ic