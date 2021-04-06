finalList = []
tempVarCount = 0


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

    def get_new_temp_var():
        global tempVarCount
        tempVarCount += 1
        return "var" + str(tempVarCount)

    def add_to_list(CODE):
        global finalList
        finalList.append(CODE)

    def print_info(self):
        print("{} = {} {} {}".format(self.dest, self.op1, self.operator,
                                     self.op2))


def print_three_address_code():
    global finalList
    for i in finalList:
        print("{} = {} {} {}".format(i.dest, i.op1, i.operator, i.op2))

    #  def __init__(self, dest="", src1="", src2="", op=""):
    #      self.dest = dest
    #      self.src1 = src1
    #      self.src2 = src2
    #      self.op = op
