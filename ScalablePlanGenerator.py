from PDDLAccessor import *
from WorldInterface import *
import GiantTortoise
import PlanApi
import ProblemWriter
import pprint
import Critic

class ScalablePlanGenerator:
    def __init__(self, data, planApi = PlanApi.Cloud_Planner_Api, tmpProbnm = "tmp/tmpProb.pddl", tmpDomnm = 'tmp/tmpDom.pddl', seed = '', tensionCurve = ([0,1,2,3,4,5,6,7],[0,1,2,4,6,5,2.5,0])):
        world = data[0]
        domain = data[1]
        costLexicon = data[2]

        self.writer = ProblemWriter.PddlProblemWriter(domain)
        self.world = json.load(open(world))
        self.planner = planApi(domain, tmpProbnm)
        self.tmpProp = tmpProbnm
        self.tmpDom = tmpDomnm
        self.lex = costLexicon
        self.tensionCurve = tensionCurve

        #possible issue here with having to make a problem first...
        #this line seems to break the system for the cloud-planer, todo: investigate
        self.custom_problem(self.world, tmpProbnm)
        problemS = fileToString(tmpProbnm)
        self.giantTortoise = GiantTortoise.GiantTortoise(domain, problemS, seed)
        #both giantTortoise and problem writher has a pddlcontroller.
        #todo: it should be investigated weather the pddlcontroler could be un-objectified and weather the essential components can be shared
        self.pddlcontroler = self.writer.pdc
        self.cement_dom()

    def update_problem_address(self, problem):
        self.planner.prob = problem
        self.planner.updateParams()

    def update_domain_address(self, domain):
        self.planner.dom = domain
        self.planner.updateParams()

    def run_planner(self, show = False ):
        return self.planner.get_plan(show)

    def custom_problem(self, new_world, prob_name, goal = "", metric = ""):
        #print(f"type {type(self.planner)}")
        if (metric == "" and type(self.planner) is PlanApi.Cloud_Planner_Api):
            metric = "(:metric minimize (total-cost))\n"
            pass
        #pprint.pprint(new_world)
        temp = self.writer.unwrap_dict(new_world)
       # pprint.pprint(temp[1])
        self.writer.create_problem_file(prob_name, temp[0], temp[1], goal, metric)
        self.update_problem_address(self.tmpProp)

    #todo: domain and in particular action-reduction relevance is to be examinated
    """
    def custom_domain(self, actions):
        dom = self.writer.domain.partition('\n(:action')
        result = dom[0]
        for a in actions:
            tmp = '\n(:action ' + a +'\n    '
            pff = getSection(a,dom[2])
            if pff == '':
                continue
            result = result + tmp + pff
        result = result + '\n)'
        f = open(self.tmpDom,'w')
        f.write(result)
        f.close()
        self.update_domain_address(self.tmpDom)

    def get_actions(self, chars):
        result = []
        for char in chars:
            if 'actions' in char:
                for action in char['actions']:
                    if action not in result:
                        result.append(action)
        return result
    """
    def cement_dom(self):
        dom = self.writer.domain
        f = open(self.tmpDom,'w')
        f.write(dom)
        f.close()
        self.update_domain_address(self.tmpDom)

    def graded_scalable_story(self, c, maxDNALength, show = False, normalize_critic = True):
        tmp = self.scalable_plan_from_chromosome(c, maxDNALength, show)
        score = self.critic_holder(tmp ,normalize= normalize_critic)
        return (tmp,score,c)

    # inputs:
    # nos = number of stories, breeders = how big a pool should be parents for the next generation, masterGenes = how many of the best breeders should move on to next generation
    # generations = max no of generations to run the algorithm for, maxGeneLength = the cutoff length of dna strands in a chromosome
    # acceptanceCriteria = is a number given for cutting the algorthim short/early if a satisfactory story has been found, set to negative to run through full no of generations
    # returns:
    # a list of tupples containing (plan,chromosome,grade)

    def gene_story(self, noS = 5, breeders = 15, masterGenes = 5, noC = 20, maxGenerations = 100, maxDNALength = 10, acceptanceCriteria = -1, normalize_critic = True, show = False):
        storyBook = []
        rejects = []
        arrangedStories = []

        for gen in range(maxGenerations):
            if (len(arrangedStories) == 0):
                arrangedStories = self.the_new_batch(breeders,maxDNALength,normalize_critic)
                print("the new batch!")

            print(gen)
            
            #genes = copy.deepcopy(arrangedStories[:masterGenes])
            #genes = genes + self.split_story_dna2(arrangedStories[:breeders])
            genes = self.split_story_dna2(arrangedStories[:breeders])
            nextGen = arrangedStories[:masterGenes]
            #print( nextGen)

            kids = 0
            while ((kids < noC and len(nextGen) < noC + masterGenes) or len(nextGen) <= masterGenes):
                #print(f"ping {len(nextGen)} kids, attempts {kids}")
                if (len(genes) >= 1):
                    g = random.choice(genes)
                else:
                    g = genes[0]
                g = self.giantTortoise.mutate_dna(g[2], genes)
                addit = True

                #is the dna already represented in the generation -don't bother adding it
                for p in nextGen:
                    if(self.giantTortoise.dna_is_same(p[2], g)):
                        addit = False
                        break
                            

                """
                """
                #is the dna in the pool of rejects -don't bother adding it
                for r in rejects:
                    if(self.giantTortoise.dna_is_same(r, g)):
                        addit = False
                        break

                if addit:
                    g = self.graded_scalable_story(g, maxDNALength, show)
                    
                    if (g[0] == '' or g[1] >= 2):
                        rejects.append(g[2])
                    else:
                        goforit = True
                        for s in nextGen:
                            if g[0] == s[0]:
                                goforit = False
                                break
                        if (goforit):
                            nextGen.append(g)
                kids += 1

            nextGen

            #if(not (len(nextGen) < noC + masterGenes)):
            #    pass
            storyBook = []
            arrangedStories = []
            for s in nextGen:
                if not self.contains_duplicate_dna(s,storyBook):
                    storyBook.append(s)

            storyBook.sort(key = sortSecond)

            n = 0
            #print("grades {")
            for story in storyBook:
                grade = story[1]
                goalgene= self.giantTortoise.makeGoalGene(story[2])
            #    print(f"{goalgene}")
            #    print("grade")
                #if the grade of the story is sufficiently bad, add it to rejects, maybe kick it..
                if (grade >= 2):
                    rejects.append(story[2])
                    if (len(arrangedStories) < breeders):
                        #arrangedStories.append(story)
                        #arrangedStories = arrangedStories + self.the_new_batch((breeders - len(arrangedStories)), maxDNALength, normalize_critic)
                        arrangedStories = copy.deepcopy(storyBook)
                        break
                #if a story is good enough end the genetic algorithm early, default is 0.02    
                if(grade < acceptanceCriteria):
                    n += 1
                    if (n == noS):
                        return storyBook
                arrangedStories.append(story)
            #print("}\n")
            #print(len(arrangedStories))

            #print()
        return arrangedStories


    def the_new_batch(self, n, maxDNALength,normalize_critic):
        result = []    
        for i in range(n):

 #           t = [['']]
#            while t[0] == ['']:
            c = self.get_chromosome(maxDNALength)
            t = self.graded_scalable_story(c,maxDNALength, normalize_critic=normalize_critic)
  #              print(t[0])
            
            result.append(t)
            
            #arrangedStories.append(['',1.99,c])
        return result

    #if a dna consists of multiple dnas this splits them and returns a list of split dnas
    #the idea is that a good gene might pop op next to a less than good one and splitting them makes it more likely to get the good stuff
    def split_story_dna(self, stories):
        dnaNo = len(stories)
        result = []
        for strandNo in range(dnaNo):
            if (len(stories[strandNo][2]) > 0):
                temp = copy.deepcopy(stories[strandNo][2])
                for g in temp:
                    story = ([""],2,[g])
                    result.append(story)
        return result


    def split_story_dna2(self,stories):
        result = []
        for story in stories:
            if (len(story[2]) > 1):
                temp = copy.deepcopy(story[2])
                for gene in temp:
                    t = ([""],2,[gene])
                    result.append(t)
            else:
                result.append(story)
        return result

    def scalable_plan_from_chromosome(self, c, max = 15,show = False):
        nwa = self.make_tiny_world_from_chomosome(c, max)
        goal = self.giantTortoise.makeGoalGene(c)
        self.custom_problem(nwa, self.tmpProp, goal)
        plan = self.run_planner(show)
        result = plan_splitter(plan)
        if (show):
            print(f"goal: {goal}\nplan: {result}")
        return result

    def get_chromosome(self, max = -1):
        result = self.giantTortoise.mk_random_dna(max)
        #print(result)
        return result
    
    def make_tiny_world_from_chomosome(self, chromos, n=10):
        result = {}
        tmp = self.list_of_stuff_to_put_in_world(chromos, n)


        for i in tmp:
            t = get_t(self.world,i)
            if t not in result:
                result[t] = [get_smth(self.world, i, t)]
            else:
                result[t].append(get_smth(self.world, i, t))

        return result

    def list_of_stuff_to_put_in_world(self, chromosome, n):
        result = []
        for signifier in self.giantTortoise.thesaurus:
            temp = self.giantTortoise.digout_dna_by_Signifier_from_chromosome(signifier, chromosome)
            if (len(temp) < n):
                no = len(temp)
            else:
                no = n
            for x in range(0,no):
                if self.giantTortoise.thesaurus[signifier][temp[x]] not in result:
                    result.append(self.giantTortoise.thesaurus[signifier][temp[x]])
        return result
    
    def critic_holder(self, plan, normalize =True, overwhelmingFailureint = 2):
        if plan == ['']:
            return overwhelmingFailureint
        plancurve = self.plan_to_curve(plan)
        if (plancurve == ([0], [0])):
            return overwhelmingFailureint
        result = Critic.curve_comparer(plancurve,self.tensionCurve, normalize= normalize)
        
        divi = (len(plancurve[0]))
        result = result/divi
        if result < 0:
            result = 2
        return result

    def plan_to_curve(self, plan):
        x = [0]
        y = [0]
        for action in plan:
            a = action.split()[0]
            lex = json.load(open(self.lex))
            if (a in lex['plan']):
                x.append(x[len(x) -1] + lex['plan'][a][0])
                y.append(y[len(y)-1] + lex['plan'][a][1])
        result = (x,y)
        #print(result)
        return result

    def contains_duplicate_dna(self, story, dnaList):
        for i in dnaList:
            #print(i)
            if(self.giantTortoise.dna_is_same(i[2],story[2])):
                return True
        return False

def sortSecond(e):
    return e[1]

"""
testing stuff
"""
dom = "Resource/redcapdomoriginal.pddl"
world = "Resource/redCapWorldoriginal.json"

dom2 = "Resource/redcapdom.pddl"
world2 = "Resource/redCapWorld.json"

dom3 = "Resource/redcapdomExpanded.pddl"
world3 = "Resource/redCapWorldExpanded.json"

dom4 = "Resource/grimmFairyTale.pddl"
world4 = "Resource/hanselAndGrethelWorld.json"

l1 = "Resource/RedRidingLex.json"


data= (world,dom,l1)
data2 = (world2,dom2,l1)
data3 = (world3,dom3,l1)
data4 = (world4,dom4,l1)


spg = ScalablePlanGenerator(data3, planApi=PlanApi.FD_Api)

#chars = spg.world['- character']
#tmpactions = spg.get_actions(chars)
#spg.custom_domain(tmpactions)



#plan = spg.run_planner()
#dna = spg.get_chromosome(max = 15)
#print(dna)
#pprint.pprint(nwa)
#plan = spg.scalable_plan_from_chromosome(dna)

"""
spg.custom_problem(spg.world,spg.tmpProp,"(inside redcap bigbadwolf) (issaved redcap)")#(whereabouts moms_house redcap) (issaved grandma) (isdead hunter)")# (inventory cake grandma) (atloc wine village)")

plan = spg.run_planner(True)
print(plan)
spg.custom_problem(spg.world,spg.tmpProp,"(whereabouts moms_house grandma)")

plan = spg.run_planner(True)
print(plan)
#story = (plan, spg.critic_holder(plan))
#print(story)
"""
"""
spg.custom_problem(spg.world,spg.tmpProp,"(isset troth_with_rocks cake_and_wine)", metric="(:metric minimize (total-cost))\n")
spg.custom_problem(spg.world,spg.tmpProp,"(not (issick grandma)) (issaved grandma) (issaved redcap)", metric="(:metric minimize (total-cost))\n")

plan = spg.run_planner()

print(plan)
print()
spg.custom_problem(spg.world,spg.tmpProp,"(isdead bigbadwolf) (not (issick grandma))", metric="(:metric minimize (total-cost))\n")

plan = spg.run_planner()

print(plan)
print()
"""
"""
spg.custom_problem(spg.world,spg.tmpProp,"(following hansel dad) (whereabouts deep_forrest grethel)", metric="(:metric minimize (total-cost))\n")

plan = spg.run_planner(True)

print(plan)
print()

"""
stories = spg.gene_story(maxGenerations=50, acceptanceCriteria= 1.13e-10, noS= 2, noC=20, maxDNALength=7)#, normalize_critic= False)

for s in stories:
    print()
    pprint.pprint(s[0])
    print(s[1])