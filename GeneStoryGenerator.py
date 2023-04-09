from PDDLAccessor import *
from WorldInterface import *
import GiantTortoise
import PlanApi
import ProblemWriter
import Critic

class GeneStoryGenerator:
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

        self.custom_problem(self.world, tmpProbnm)
        problemS = fileToString(tmpProbnm)

        self.giantTortoise = GiantTortoise.GiantTortoise(domain, problemS, seed)
        self.pddlcontroler = self.writer.pdc
        self.cement_dom()

    #update the problem file address for the planner api
    def update_problem_address(self, problem):
        self.planner.prob = problem
        self.planner.updateParams()

    #update the domain file address for the planner api
    def update_domain_address(self, domain):
        self.planner.dom = domain
        self.planner.updateParams()

    #runs the third party planner through the api
    def run_planner(self, show = False ):
        return self.planner.get_plan(show)

    #uses the problem writer to make a custom PDDL problem file
    def custom_problem(self, new_world, prob_name, goal = "", metric = ""):
        """
        if (metric == "" and type(self.planner) is PlanApi.Cloud_Planner_Api):
            metric = "(:metric minimize (total-cost))\n"
            pass
        """
        temp = self.writer.unwrap_dict(new_world)
        self.writer.create_problem_file(prob_name, temp[0], temp[1], goal, metric)
        self.update_problem_address(self.tmpProp)

    #this is for making sure the domain is the right one
    def cement_dom(self):
        dom = self.writer.domain
        f = open(self.tmpDom,'w')
        f.write(dom)
        f.close()
        self.update_domain_address(self.tmpDom)

    #returns a "story", a tuple of a plan, a score and the chromosome
    def graded_scalable_story(self, c, maxDNALength, show = False, normalizeCritic = True):
        tmp = self.plan_from_chromosome(c, maxDNALength, show)
        score = self.critic_holder(tmp ,normalize= normalizeCritic)
        return (tmp,score,c)

    # takes:
    # nos = number of stories, breeders = how big a pool should be parents for the next generation, masterGenes = how many of the best breeders should move on to next generation
    # generations = max no of generations to run the algorithm for, maxGeneLength = the cutoff length of dna strands in a chromosome
    # acceptanceCriteria = is a number given for cutting the algorthim short/early if a satisfactory story has been found, set to negative to run through full no of generations
    # returns:
    # a list of tupples containing (plan,chromosome,grade) aka stories

    def gene_story(self, initial = 10, noS = 5, breeders = 10, masterGenes = 5, noC = 20, maxGenerations = 100, maxDNALength = 10, acceptanceCriteria = -1, normalizeCritic = True, show = False):
        storyBook = []
        rejects = []
        arrangedStories = []

        for gen in range(maxGenerations):
            if (len(arrangedStories) == 0):
                arrangedStories = self.the_new_batch(initial,maxDNALength,normalizeCritic)
                print("the new batch!")

            genes = copy.deepcopy(arrangedStories[:breeders])
            genepool = genes + self.split_story_dna(genes)
            
            currentG = []
            for g in genes:
                gg = self.giantTortoise.makeGoalGene(g[2])
                currentG.append(gg)
            
            nextGen = arrangedStories[:masterGenes]

            print(f"generation {gen}, genepool {len(genepool)}, blacklist {len(rejects)}")
            kids = 0

            while (kids < noC):

                #genepool = copy.deepcopy(genes)
                
                if (len(genepool) > 1):
                    g = random.choice(genepool)
                    genepool.remove(g)
                else:
                    g = genepool[0]
                
                g = self.giantTortoise.mutate_dna(g[2], genepool)
                addit = True

                #print(f"g {g}")
                #print(f"g {self.giantTortoise.makeGoalGene(g)}")
                #is the dna already represented in the generation -don't bother adding it
                for p in nextGen:
                    if(self.giantTortoise.dna_is_same(p[2], g)):
                        addit = False
                        break

                #is the dna in the pool of rejects or effectively a clone of one of the parents -don't bother adding it
                if addit:
                    gg = self.giantTortoise.makeGoalGene(g)
                    if(gg in rejects or gg in currentG):
                        addit = False

                #if the dna is valid...
                if addit:
                    #... write up the story
                    g = self.graded_scalable_story(g, maxDNALength, show)
                    
                    #if the story is empty or REALLY bad reject it
                    if (g[0] == '' or g[1] >= 2):
                        bg = self.giantTortoise.makeGoalGene(g[2])
                        if (bg not in rejects):
                            rejects.append(bg)

                    
                    else:

                        #if a similar story is currently in the generation, don't add it
                        for s in nextGen:
                            if g[0] == s[0]:
                                addit = False
                                break
                        
                        if (addit):
                            nextGen.append(g)
                kids += 1

            
            storyBook = []
            arrangedStories = []
            #there is still a chance for twins, hense the culling
            for s in nextGen:
                if not self.contains_duplicate_dna(s,storyBook):
                    storyBook.append(s)

            storyBook.sort(key = sortSecond)

            n = 0
            for story in storyBook:
                grade = story[1]
            
                #if the grade of the story is sufficiently bad, add it to rejects, maybe kick it..
                if (grade >= 2):
                    bg = self.giantTortoise.makeGoalGene(story[2])
                    if (bg not in rejects):
                            rejects.append(bg)
                    if (len(arrangedStories) < breeders):
                        arrangedStories = copy.deepcopy(storyBook)
                        break
                #if enough stories are good enough end the genetic algorithm early
                if(grade < acceptanceCriteria):
                    n += 1
                    if (n == noS):
                        return storyBook
                arrangedStories.append(story)

        return arrangedStories

    #makes a list of n stories
    def the_new_batch(self, n, maxDNALength,normalizeCritic):
        result = []    
        for i in range(n):
            c = self.get_chromosome(maxDNALength)
            t = self.graded_scalable_story(c,maxDNALength, normalizeCritic=normalizeCritic)      
            result.append(t)

        return result

    #if a dna consists of multiple dnas this splits them and returns a list of split dnas
    #the idea is that a good gene might pop op next to a less than good one and splitting them makes it more likely to get the good stuff
    def split_story_dna(self,stories):
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

    def plan_from_chromosome(self, c, max = 15,show = False):
        nwa = self.make_tiny_world_from_chomosome(c, max)
        goal = self.giantTortoise.makeGoalGene(c)
        self.custom_problem(nwa, self.tmpProp, goal)
        plan = self.run_planner(show)
        result = plan_splitter(plan)
        if (show):
            print(f"goal: {goal}\nplan: {result}")
        return result

    #gets a random chromosome from the giantTortoise
    def get_chromosome(self, max = -1):
        result = self.giantTortoise.mk_random_dna(max)
        return result

    #makes a world from the chromosome with maximum n of each type*
    #*the maximum may varry because of dependencies between certain items e.g. : holders of a certain thing, a location that a person is located at etc.
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
    
    #this is just a wrapper for returning an int, using the critic to compare the likenes of two curves represented by two tuples of two lists of ints ([x],[y])
    def critic_holder(self, plan, normalize = 'both', overwhelmingFailureint = 2):
        if plan == ['']:
            return overwhelmingFailureint
        plancurve = self.plan_to_curve(plan)
        if (plancurve == ([0], [0])):
            return overwhelmingFailureint
        
        result = Critic.curve_comparer(plancurve,self.tensionCurve, normalize= normalize)
        
        divi = (len(plancurve[0]))
        result = result/divi
        #this shouldn't really be happening
        if result < 0:
            result = 2
        return result

    #takes a plan and transforms it into a "curve" ([x],[y])
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
        return result

    def contains_duplicate_dna(self, story, dnaList):
        for i in dnaList:
            if(self.giantTortoise.dna_is_same(i[2],story[2])):
                return True
        return False


#why didn't I just write this as an anonymous function?
def sortSecond(e):
    return e[1]