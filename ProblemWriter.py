"""
a class for writing a PDDL problem file to go with a PDDL domain file from a "world" in the form of a dictx
Auth: Jakob Ehlers
"""
#todo: un-objectify this class and turn it into a list of methods
import PDDLController
import PDDLAccessor

class PddlProblemWriter:
    def __init__(self, domain):
        self.pdc = PDDLController.PDDLController(domain)
        file = open(domain)
        self.domain = file.read()
        file.close()
        self.domainName = self.domain.partition("domain")[2].partition(")")[0].split()[0]
        self.state = []

    #constructs a header        
    def make_header(self, name):
        header = "(define (problem "+name+") (:domain "+self.domainName+")\n"
        return header


    #sometimes I wish I was writing in a functional language
    def unwrap_dict(self, dictionary):
        keys = dictionary.keys()
        keys = list(keys)

        probjects = ""
        initial = ""
        for k in keys:
            probjects = probjects + self.probject_string(k, dictionary[k])
            initial = initial + self.predicate_string(dictionary[k])
        return (probjects, initial)

    #takes a dictionary and if it contains a list of predicates, it will construct strings of predicates for use in the problem state 
    def predicate_string(self, thing):
        result = ""
        for t in thing:
            if "predicates" in t:
                preds = t["predicates"]
                for k in preds:
                    #if the list of the key predicate is empty, a check should be made to see if the predicate in question only needs one var
                    if (type(preds[k]) == int):
                        if (preds[k] > 0):
                            temp = "    " + parenthesise(k + " "+ t["name"])
                            result = result + temp + "\n"
                    else:
                        for x in preds[k]:
                            temp = "    " + parenthesise(k + " " + x + " "+ t["name"])
                            result = result + temp + "\n"
        return result

    #takes a object type as a string and a list of objects that belong to the given type and returns a space seperated string of objects finalized by the type 
    def probject_string(self, probT, l):
        result = "    "
        for i in l:
            result = result + i["name"] + " "
        result = result + probT + "\n"
        return result

    #takes a file path name, problem objects, and an initial state as strings and constructs a PDDL problem file to be saved under the path name
    # a goal and a metric can be supplied if so desired
    def create_problem_file(self, path, probjects, initial, goals = "", metric = ""):
        name = PDDLAccessor.name_extractor(path)
        file = open(path, "w")
        file.write(self.make_header(name))
        file.close()
        file = open(path, "a")
        file.write("(:objects\n")
        file.write(probjects)
        file.write(")\n(:init\n")
        if metric != "":
            file.write("    (= (total-cost) 0)\n")
        file.write(initial)
        file.write(")\n(:goal\n    (and\n    "+goals+"\n    )\n)\n")
        if metric != "":
            file.write(metric)
        file.write(")")
        file.close

#takes a string and returns it withing a parenthesis
# if only this had been added sooner, it would probably have seen even more use
def parenthesise(str):
    return "(" + str + ")"
