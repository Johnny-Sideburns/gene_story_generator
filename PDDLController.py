"""
Class for holding domain info and applying it to pddl problems stuff
auth: Jakob Ehlers
"""
#todo: un-objectify this class and turn it into a list of methods
import PDDLAccessor
from IntermediateParser import *

#I decoupled the problem from this part of the code, if there is residue it is merely superstition on the programmers part...
class PDDLController:
    def __init__(self, domain):
        self.domainFile = domain
        self.domain = PDDLAccessor.fileToString(domain)
        #set up dicts for nested domain types
        self.pddltypes = self.mapTyps2("types", self.domain)
        
        #loop for creating the list of dicts of actions
        #reworking
        self.actions = []
        n = self.domain.count("(:action ")
        tempDom = self.domain
        
        while (n > 0):
            tempDom = tempDom.partition("(:action ")[2]
            action = PDDLAccessor.parseAction(tempDom.partition("\n")[0], self.domain)
            self.actions.append(action)
            n -= 1
        #loop for creating the list of domain predicates
        pred = PDDLAccessor.getSection("predicates", self.domain)
        predicates = pred.split('\n')
        self.predicates = []
        for x in predicates:
            temp = x.strip()
            if (len(temp) > 1):
                self.predicates.append(temp)

    #itterates the list of actions and returns an action with a matching name, and False on failure
    def getAction(self, name):
        for x in self.actions:
            if (x.get("name") == name):
                return x
        print("error: no such action name: " + name)
        return False

    #returns a dict with concrete parameters for replacing the variables
    def adjustParameters(self, action, params):
        paramargs = action.get("parameters") 
        result = {}
        params = params.partition(" ")[2]
        n = paramargs.count("?")
        x = 0
        while (x < n):
            paramargs = paramargs.partition("?")[2]

            if (paramargs.count(" ") > 0):
                s = "?" + paramargs.partition(" ")[0]
                result[s] = params.partition(" ")[0].replace(")", "")
            elif (paramargs.count(")") > 0):
                s = "?" + paramargs.partition(")")[0]
                result[s] = params.partition(")")[0]

            params = params.partition(" ")[2]
            x += 1

        return result

    #returns a dict of the different types in the domain, well actually only the super and sub-types
    def mapTyps2(self, section, target):
        typs = PDDLAccessor.getSection(section, target).partition(')')[0].strip().split('\n')
        result = {}
        for l in typs:
            if (l.__contains__("-")):
                kvpair = l.partition("-")
                k = "-" + kvpair[2].partition("\n")[0]
                v = kvpair[0].rpartition("\n")[2].split()
                result[k] = v
            else:
                result['- '+(l.strip())] = []

        return result

    #a slightly more flexible version of applyAction, that applies an action to a given state
    def apply_action_to_state(self, actionString, state, thesaurus):
        name = actionString.partition("(")[2].partition(" ")[0]
        action = self.getAction(name)
        #adds a dict with substitutions for the action parameters to the excisting dict of pddl types
        lookUpBook = {**self.adjustParameters(action, actionString), **thesaurus}
        #check for precondition satisfaction
        if (applyFunction(action.get("precondition"), lookUpBook, precondCheck, state,True,andOp)):
            #applying the allowed change to state
            state = applyFunction(action.get("effect"), lookUpBook, applyEffect, state, state, andOp)
            return state
        #on failure:
        print("action "+ actionString + " NOT allowed" )
        return ""

    #applies the current state (:init...) to the pddl problem file
    #can and should be disconnected from the class
    #pretty sure this isn't in use anywhere
    def writeChange(self):
        tmp = self.problem
        tmpfirst = tmp.partition("init")[0]+"init"
        tmplast = tmp.partition("(:goal")[2]
        result = tmpfirst + "\n" + self.state + ")\n(:goal" + tmplast
        file = open(self.problemFile, "w")
        file.write(result)
        file.close()

    #takes the name of an action and reconstructs it from the deconstructed dict version to it's original (pddl)string format
    def action_to_string(self, action_name):
        action = self.getAction(action_name)
        if not action:
            return False

        param = action['parameters']

        prec = applyFunction(action['precondition'], '', listyfy, '', [], andOp)
        precondition = '(and'
        for p in prec:
            precondition = precondition + ' ' + p
        precondition = precondition + ')'
        
        eff = applyFunction(action['effect'], '', listyfy, '', [], andOp)
        effect = '(and'
        for e in eff:
            effect = effect + ' ' + e
        effect = effect + ')'

        result = '(:action ' + action['name'] + '\n    :parameters ' + param + '\n    :precondition ' + precondition + '\n    :effect ' + effect + '\n)'
        return result


#testing stuff beyond this point

"""
import pprint
domainF = "tmp/AdventureDomCopy.pddl"
problemF = "tmp/AdventureProbCopycopy.pddl"

pc = PDDLController(domainF)

print("\npredicates:")
pprint.pprint(pc.predicates)
print("\ntypes:")
pprint.pprint(pc.pddltypes)
print("\nobjects:")
pprint.pprint(pc.probjects, sort_dicts= False)
"""