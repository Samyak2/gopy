# Representation: '''Destination, operand1, operand2, operator'''

tempVarBaseName = "var"
tempVarCount = 0

# finalList is a list which will store the complete intermediate code
finalList = {"main": []}
quadruple = {"main": -1}
nextQuad = {"main": 0}


# Gives the temp variable
def get_new_temp_var():
    global tempVarCount
    tempVarCount += 1
    return tempVarBaseName + str(tempVarCount)


def increment_quad(func_name):
    global quadruple
    quadruple[func_name] = nextQuad[func_name]
    nextQuad[func_name] += 1
    return quadruple[func_name]


def getNextQuad(functionName):
    return nextQuad[functionName]


def get_code_length(func_name):
    return quadruple[func_name]


def add_tac(func_name, dest, src1, src2, op):
    global finalList
    increment_quad(func_name)
    finalList[func_name].append([dest, src1, src2, op])


def create_new_function_code(func_name):
    global finalList, quadruple
    finalList[func_name] = []
    quadruple[func_name] = -1
    nextQuad[func_name] = 0


def print_list():
    for i in finalList.keys():
        print("{} : ".format(i))
        for j in range(len(finalList[i])):
            print("%5d:\t" % j, finalList[i][j])
