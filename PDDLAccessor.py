"""
Methods for accessing the pddl files
Auth: Jakob Ehlers
"""
import re
import IntermediateParser

#returns a file as string opening and closing    
def fileToString(fileName):
    temp = open(fileName)
    result = temp.read().lower()
    temp.close()
    return result

#returns a given section by counting parenthesis, n value should be set to 0 if starting outside a parenthesis
def getSection(name, target, n = 1):
    temp = target.partition(name)[2].lstrip()
    temp = re.sub(r';.*', '', temp)
    result = ""
    for x in temp:
        result = result + x
        if (x == "("):
            n += 1
        elif (x == ")"):
            n -= 1
        if (n < 1):
            break
    return result

#returns a dict modelled on "PDDL (:action..."
def parseAction(name, domain):
    actionString = getSection("action " + name, domain)
    if (actionString == ""):
        print("no such action")

    parameters = getSection("parameters", actionString, 0)
    precondition = getSection("precondition", actionString, 0)
    effect = getSection("effect", actionString,0)

    params = IntermediateParser.whiteSpaceMatters(parameters)
    preco = IntermediateParser.parsePddlExpression(precondition)
    effe = IntermediateParser.parsePddlExpression(effect)

    action =   {"name" : name,
                "parameters" : params,
                "precondition" : preco,
                "effect" : effe
                }
    return action

#self explanatory
def copyFile(source, newFile):
    openFile = open(source)
    fileContent = openFile.read()
    openFile.close()
    openFile = open(newFile, "w")
    openFile.write(fileContent)
    openFile.close()

#replaces the goal of a problem
def changeGoal(prob, newGoal, newFile = ""):
    if (newFile == ""):
        newFile = prob
    file = open(prob)
    tmp = file.read()
    file.close()
    tmp = tmp.partition("(:goal")
    result = tmp[0] + tmp[1] + "\n    (and\n        " + newGoal + "\n    )\n)\n)"
    file = open(newFile, "w")
    file.write(result)
    file.close()

#takes a problem and a replaces the state
#if needed it can save it as a new file
def changeState(prob, newState, newFile = ""):
    if (newFile == ""):
        newFile = prob
    file = open(prob)
    tmp = file.read()
    file.close()
    tmp = tmp.partition("(:init")
    result = tmp[0] + tmp[1] + "\n" + newState + ")\n(:goal" + tmp[2].partition("(:goal")[2]
    file = open(newFile, "w")
    file.write(result)
    file.close()

#takes: a plan 
# and splits it up nicely
def plan_splitter(plan):
    result = re.sub(r'(;.*)', '', plan)
    result = result.strip()
    result = result.split('\n')
    return result

#this is used for testing
def printPlan(plan):
    openPlan = open(plan)
    print(openPlan.read())
    openPlan.close()

#takes: a file path as a string
#returns: a string of the file name without type indication, barring multiple periods in file name
def name_extractor(path):
    name = path.rpartition('/')[2].partition('.')[0]
    return name

#takes: a list of lists and a list of list of lists
# and checks if the former is present in the latter
#returns: bool
def lol_in_list_of_lol(l1, l2):
    for element in l2:
        k = 1
        for pos in range(0, len(l1)):
            if (list(l1[pos]) == list(element)[pos]):
                k += 1
                if (k == len(element)):
                    return True
    return False
                            
    

"""
#testing stuff beyond this point

import pprint
domainF = "tmp/AdventureDomCopy.pddl"
problemF = "tmp/AdventureProbCopycopy.pddl"

domain = fileAsString(domainF)
actions = []
n = domain.count("action")
tempDom = domain
while (n > 0):
    tempDom = tempDom.partition("action ")[2]
    action = parseAction(tempDom.partition("\n")[0], domain)
    actions.append(action)
    n -= 1

for x in actions:
    pprint.pprint(x, sort_dicts= False)
    pass
"""