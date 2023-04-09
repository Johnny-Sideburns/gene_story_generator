"""
Let's try to define the genome for accomodating a genetic algorithm
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

        self.setup(problemS)
        
        if (seed != ""):
            random.seed(seed)

    #method for setting up the class variables
    #takes a pddl problem as a string

    def setup(self, problemS):    
        
        #this part contextualizes different theoretically achievable PDDL problem goals.
        #this is done by going through domain action effects
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

    #takes two chromosomes, and replaces a random chromosome from the first with a chromosome of the seccond
    def replace_chrom(self, dna1, dna2):
        roll = random.randint(0, len(dna1) -1)
        roll2 = random.randint(0, len(dna1[roll]) -1)
        roll3 = random.randint(0, len(dna2) -1)
        result = copy.deepcopy(dna1)
        result[roll][roll2] = copy.copy(dna2[roll3][roll2])
        return result
    
    #takes two chromosomes, and makes them into one chromosome consisting of two chromosomes
    def join_dna(self, host, genes, n = 0):
        #this limits how many chromosomes will be allowed to be joined together
        #and how many times to try doing it unsuccesfully
        if (len(host) > 3 or n > 50):
            return self.mutate_dna(host,genes, random.randint(0,89))
        
        doner = random.choice(genes)[2]
        donation = random.choice(doner)
        child = copy.deepcopy(host)

        for c in child:
            if (self.same_chrom_goals([c],[donation])):
                return self.join_dna(host,genes, n+1)
        
        child.append(donation)
        
        return child


        """
        if (len(dna1) > 3 or n > 7):
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
        """

    #takes a chromosome and spawns a new random chromosome alongside it
    def dna_mitosis(self, dna, n = 0):
        result = copy.deepcopy(dna)
        if (len(dna) > 3):
            roll0 = random.randint(0, len(result) -1)
            result.pop(roll0) 
        roll = random.choice(result)
        temp = self.mutate_dna_randomly([roll])
        if (self.same_chrom_goals(temp, result)):
            return self.dna_mitosis(result)
        else:
            result = result + temp
            #print(self.makeGoalGene(result))
            return result

    #takes a chromosome and shuffles a random gene
    def mutate_dna_randomly(self, dna):
        roll = random.randint(0,len(dna)-1)
        roll2 = random.randint(0,len(dna[roll])-1)
        temp = copy.deepcopy(dna)
        random.shuffle(temp[roll][roll2])
        return temp
    
    #takes two chromosomes and takes genes at random from each to construct a new chromosome
    def crossover_into_one(self, chromo, genepool):
        child = []
        if (len(chromo) > 1):
            mom = [random.choice(chromo)]
        else:
            mom = chromo

        dad = random.choice(genepool)[2]

        if (len(dad) > 1):
            dad = [random.choice(dad)]
        

        for n in range (len(mom[0])):
            roll = random.randint(0,1)
            if (roll < 1):
                child.append(mom[0][n])
            else:
                child.append(dad[0][n])
    

        return [child]
    
    def crossover_elaborate(self, chromo, genepool, d = 0):
        child = copy.deepcopy(chromo)
        dad = random.choice(genepool)[2]

        if (d > 10):
            roll = random.randint(50,99)
            return self.mutate_dna(chromo, genepool, roll)

        for x in child:
            for n in range(len(chromo[0])):
                roll = random.randint(0,1)
                if (roll < 1):
                    y = random.choice(dad)
                    x[n] = y[n]

        if (len(child) > 1):
            for n in range(len(child)-1):
                for i in range(len(child)):
                    if (i > n):
                        if(self.same_chrom_goals([child[n]],[child[i]])):
                            return self.crossover_elaborate(chromo, genepool, d + 1)

        return child

    #randomizing between a couple of different ways to mutate a dna strand
    def mutate_dna(self, chrom, genes, n = -1):
        #print(f"in = {self.makeGoalGene(chrom)}")
        if (n < 0):
            n = random.randint(0,99)
    
        if (n < 10 and len(chrom) > 1):
            roll = random.randint(0, len(chrom) -1)
            result = copy.deepcopy(chrom)
            result.pop(roll)
            return result
        
        elif (n < 20):
            return self.crossover_into_one(chrom, genes)
        
        elif (n < 50):
            return self.crossover_elaborate(chrom, genes)

        elif (n < 60):
            k = random.choice(genes)[2]
            return self.replace_chrom(chrom,k)
        
        elif (n < 70):
            return self.mutate_dna_randomly(chrom)

        elif (n < 80):
            return self.mk_random_dna()
            
        elif (n < 90):
            return self.dna_mitosis(chrom)
        else:
            return self.join_dna(chrom,genes)


    #takes a dna strand and makes it into a goal-gene
    def makeGoalGene(self, dna):
        gg = ""
        for g in dna:
            gg += self.makeGene(g, self.goalPredicates) + "\n"
        return gg

    #takes two chromosomes and check if they produce the same goals
    def same_chrom_goals(self, chrom1, chrom2):
        g1 = self.makeGoalGene(chrom1)
        g2 = self.makeGoalGene(chrom2)
        return (g1 == g2)

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
        
        return result

    #if possible returns a gene of a given type from a chromosome
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