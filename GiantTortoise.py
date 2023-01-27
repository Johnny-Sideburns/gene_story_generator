"""
Let's try to make a genetic algorithm
The Giant Tortoise lost the genetic lottery by being so tasty that bringing one to London to officially be given a name proved quite challenging for the pekish sailors.
it works by using a pddlController to identify, seperate and categorize different atributes as "genes" and "dna", it also contains methods for shaking them up
Auth: Jakob Ehlers
"""
import PDDLController
from IntermediateParser import *
import random
import copy

class GiantTortoise:
    def __init__(self, domainF, problemS, seed):
        self.pc = PDDLController.PDDLController(domainF)#, problemS)
        #self.goalPredicates = self.getGoalPredicates()

        """
        #pprint.pprint(fileToString(domainF), sort_dicts= False)
        pprint.pprint(self.pc.domain, sort_dicts= False)
        print()
        pprint.pprint(self.pc.actions, sort_dicts= False)
        """
        self.setup(problemS)
        if (seed != ""):
            random.seed(seed)

    
    def setup(self, problemS):    
        pist = []
        result = []
        for action in self.pc.actions:
            pist = pist + applyFunction(action["effect"],self.pc.pddltypes, listyfy, "",pist,andOp)
        
        for effect in pist:
            if (effect.split()[0] == "(not"):
                k = 1
            else: k = 0
            for pred in self.pc.predicates:
                if (pred.count(effect.split()[k]) > 0):
                    if (k == 1):
                        temp = "(not " + pred + ")"
                        break
                    else:
                        temp = pred
                        break
            if (result.__contains__(temp) == False):
                result.append(temp)
        self.goalPredicates = result
        self.probjects = self.pc.mapTyps2("objects", problemS)
        self.thesaurus = deeper_merge_dict_of_lists(expandDict(self.pc.pddltypes, self.probjects, "- "), self.probjects)
        self.genome = [len(self.goalPredicates)] + self.mapGenome(self.thesaurus)

    #returns a list of lists of ints with the numbers shuffeled
    def mk_random_dna(self, max = -1):
        gene = []
        if (max < 1):
            for x in self.genome:
                temp = range(0,x)
                temp = list(temp)
                random.shuffle(temp)
                gene.append(temp)
        else:
            for x in self.genome:
                n = max
                if (x < max):
                    n=x
                temp = range(0, n)
                temp = list(temp)
                random.shuffle(temp)
                gene.append(temp)
        return [gene]

    #takes two dna strands, and replaces a random gene from the first with the coresponing gene of the seccond
    def mix_dna(self, dna1, dna2):
        roll = random.randint(0, len(dna1) -1)
        roll2 = random.randint(0, len(dna1[roll]) -1)
        roll3 = random.randint(0, len(dna2) -1)
        result = copy.deepcopy(dna1)
        result[roll][roll2] = copy.copy(dna2[roll3][roll2])
        return result

    def join_dna(self, dna1, genes, n = 0):
        if (len(dna1) > 2 or n > 5):
            #print("strand full")
            return self.mutate_dna(dna1, genes)
        k = random.randint(0, len(genes) -1)
        dna2 = genes[k][2]
        roll = random.randint(0, len(dna2) -1)
        
        if (not self.dna_in_dnas(dna1,[dna2[roll]])):
            result = copy.deepcopy(dna1)
            result.append(copy.deepcopy(dna2[roll]))
            return result
        n += 1
        return self.join_dna(dna1,genes, n)

    def dna_mitosis(self, dna):
        result = copy.deepcopy(dna)
        if (len(dna) > 2):
            roll0 = random.randint(0, len(result) -1)
            result.pop(roll0) 
        roll = random.randint(0, len(result) -1)
        temp = self.mutate_dna_randomly([result[roll]])
        if (self.dna_in_dnas(temp, result)):
            return self.dna_mitosis(result)
        else:
            result = result + temp
            return result

    #takes a dna strand and shuffles a random gene
    def mutate_dna_randomly(self, dna):
        roll = random.randint(0,len(dna)-1)
        roll2 = random.randint(0,len(dna[roll])-1)
        temp = copy.deepcopy(dna)
        random.shuffle(temp[roll][roll2])
        return temp

    #offline till further notice
    """
    #takes a dna strand and shuffles a random gene
    def mutate_dna_semi_randomly(self, dna, skipGenes = 0):
        roll = random.randint(skipGenes,len(dna)-1)
        random.shuffle(dna[roll])
    """

    

    #randomizing between a couple of different ways to mutate a dna strand
    def mutate_dna(self, dna, genes, i = 22000):
        n = random.randint(0,99)
        if (n < 10 and len(dna) > 1):
            roll = random.randint(0, len(dna) -1)
            result = copy.deepcopy(dna)
            result.pop(roll)
            return result
        
        elif (n < 25):
            #print("mutate")

            return self.mutate_dna_randomly(dna)
        elif (n < 45):
            #print("mix")

            k = i
            while (k == i):
                k = random.randint(0, len(genes) -1)
            return self.mix_dna(dna,genes[k][2])
        elif (n < 70):
            #print("new")
            return self.mk_random_dna()
        elif (n < 85):
            #print("split")
            return self.dna_mitosis(dna)
        else:
            #print("join")
            return self.join_dna(dna,genes)

    #creates a list of achievable goal-state expressions from action effects and domain predicates
    #depricated
    """
    def getGoalPredicates(self):
        result = []
        temp = ""
        for action in self.pc.actions:
            for effect in action["effect"]["and"]:
                ton = False
                if (type(effect) is dict):
                    #todo include when
                    if (list(effect.keys()).__contains__("not")):
                        ton = True
                        effect = effect["not"]
                    elif (list(effect.keys()).__contains__("forall")):
                        effect = effect["forall"][1]
                        print(effect)
                    else: continue
                for pred in self.pc.predicates:
                    if (pred.count(effect.split()[0]) > 0):
                        if (ton):
                            temp = "(not " + pred + ")"
                            break
                        else:
                            temp = pred
                            break
                if (result.__contains__(temp) == False):
                    result.append(temp)
        return result
    """


    #takes a dna strand and makes it into a goal-gene
    def makeGoalGene(self, dna):
        gg = ""
        for g in dna:
            gg += self.makeGene(g, self.goalPredicates) + "\n"
        return gg

    def dna_is_same(self, dna1, dna2):
        count = len(dna2)
        for genes in dna1:
            for genes2 in dna2:
                if (self.gene_is_same(genes,genes2)):
                    count -= 1
                    break
        if (count < 1):
            return True
        else:
            return False

    def dna_in_dnas(self, dna, dnas):
        for g1 in dna:
            for g2 in dnas:
                if (self.gene_is_same(g1,g2)):
                    return True
        return False

    def gene_is_same(self, dna1, dna2):
        gg1 = self.makeGoalGene([dna1])
        gg2 = self.makeGoalGene([dna2])
        if (gg1 == gg2):
            return True
        else: 
            return False

    #returns a gene from an int[] by popping the first int and picking the complying expression from the pool, and using the rest of the list as choices for substitution
    def makeGene(self, dna, pool):
        cellShell = dna[0][0]
        cellShell = pool[cellShell]
        result = self.substituteVar(cellShell, dna)
        return result

    #takes in an expression and, if no variable is given, the first ?smth variable that gets substituted with a fitting string from the thesaurus
    #maybe this should be made more general and put in the parser
    def substituteVar(self, predicate, rootdna):
        
        result = predicate
        
        dna = copy.deepcopy(rootdna)

        while (result.count("?") > 0):    
            temp = result.partition("?")
            variable = "?" + temp[2].partition(" ")[0]
            signifier = temp[2].partition("- ")[2].partition(")")[0]
            if(signifier.count(" ") > 0):
                signifier = signifier.partition(" ")[0]
            signifier = "- " + signifier


            #am I insane? why would I make this with side by side running counters, this should be done way more elegant and less fragile
            #so that instead of being mached up with the arbtrary order of creation it is more controlled
            #but until then if it works it works
            p = 1
            for x in self.thesaurus:
                if (x == signifier):
                    no = dna[p].pop(0)
                p += 1
            

            if signifier == '- ':
                print(f"sig {signifier}  no: {no}  dna: {dna}   result {result}")

            #if the type is not present in the world the action cannot be performed and the goal is empty
            if signifier not in self.thesaurus:    
                return ""
            value = self.thesaurus[signifier][no]
            result = result.replace(variable,value)

            if (result.partition(signifier)[0].count("?") < 1):
                signifier = " " + signifier
                result = result.replace(signifier, "",1)
    
        return result

    #returns a list of ints from the length of the lists of parameter possibilities of the expression
    def mapGenome(self, source):
        result = []
        for x in source:
            temp = len(source[x])
            result.append(temp)
        
        #print(f"map genome {result}")
        return result

    def digout_dna_by_Signifier_from_chromosome(self, signifier, chromosome):
        p = 1
        for x in self.thesaurus:
            if (x == signifier):
                dna = chromosome[0][p]
                return dna
            p += 1
        return False

#expand definitions so upper categories include sub's content
def expandDict(super_dict, sub_dict, prefix = ""):
    result = {}
    for x in super_dict:
        temp = []
        for k in super_dict[x]:
            key = prefix + k
            if (list(super_dict.keys()).__contains__(key)):
                for p in super_dict[key]:
                    pey = prefix + p
                    if(list(sub_dict.keys()).__contains__(pey)):
                        temp = temp + sub_dict[pey]        
            if(list(sub_dict.keys()).__contains__(key)):
                temp = temp + sub_dict[key]
        result[x] = temp

    return result

#takes two dicts of lists and merges them at a slightly deeper level as to merge lists with the same key, or you know anything else that the += operator will work on.. yay python!
def deeper_merge_dict_of_lists(d1,d2):
    for l in d2:
        if l in d1:
            d1[l] += d2[l]
        else:
            d1[l] = d2[l]
    return d1
"""
testing stuff
"""        
"""
import pprint
import PDDLAccessor

pd = "tmp/AdventureDomCopy.pddl"
pp = "tmp/AdventureProbCopycopy.pddl"

pd1 = "tmp/RedRidingHoodDom.pddl"
pp1 = "tmp/RedRidingHoodProb.pddl"

pp2 = "tmp/RedHoodProbTwo.pddl"

problemS = PDDLAccessor.fileToString(pp2)
dna = GiantTortoise(pd1, problemS, '')

pprint.pprint(dna.thesaurus, sort_dicts=False)


for x in dna.goalPredicates:
    print(x)

print()
print(dna.genome)
print()

#pprint.pprint(dna.pc.probjects)
print()
pprint.pprint(dna.pc.pddltypes)
print()
pprint.pprint(dna.goalPredicates)
"""