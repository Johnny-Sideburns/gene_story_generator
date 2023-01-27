import json
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
        #self.objects = self.define_object_types()
        
    def make_header(self, name):
        header = "(define (problem "+name+") (:domain "+self.domainName+")\n"
        return header

    def objectify(self, dictionary):
        keys = dictionary.keys()
        keys = list(keys)

        for k in keys:
            area = dictionary[k]
            for n in area:
                self.objects[k].append(n["name"])
                self.relate_area(n)

        #print(self.objects)
        #print(self.initial)
        return dictionary[k]

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

    def probject_string(self, probT, l):
        result = "    "
        for i in l:
            result = result + i["name"] + " "
        result = result + probT + "\n"
        return result

    def create_problem_file(self, path, probjects, initial, goals = "", metric = ""):
        name = PDDLAccessor.name_extractor(path)
        file = open(path, "w")
        file.write(self.make_header(name))
        file.close()
        file = open(path, "a")
        file.write("(:objects\n")
        file.write(probjects)
        file.write(")\n(:init\n")
        #this needs to be made flexible
        if metric != "":
            file.write("    (= (total-cost) 0)\n")
        file.write(initial)
        file.write(")\n(:goal\n    (and\n    "+goals+"\n    )\n)\n")
        if metric != "":
            file.write(metric)
        #file.write("(:metric minimize (total-cost))\n")
        file.write(")")
        file.close

def parenthesise(str):
    return "(" + str + ")"
"""
testing stuff        

thin = ppw.unwrap_dict(datac)
ppw.create_problem_file("OVERHERE", thin[0], thin[1])

"""

#data = json.load(open('world.json','r'))

#k = ppw.objectify(data)
#ppw.create_problem_file("experiments")
