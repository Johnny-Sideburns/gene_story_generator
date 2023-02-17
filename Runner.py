import GeneStoryGenerator
import PlanApi
import pprint
import time
import PDDLAccessor

dom = "Resource/redcapdomExpanded.pddl"
world = "Resource/redCapWorldExpanded.json"

l1 = "Resource/RedRidingLex.json"

data = (world,dom,l1)

tc = ([0,1,2,3,4,5,6,7,8,9],[0,1,2,3,5,7,8,5,2,1])
tc2 = ([0,4,5,8,13,14,16,17,18,19],[0,1,2,3,4,5,4,3,1,0])


gsg = GeneStoryGenerator.GeneStoryGenerator(data, seed = '', tensionCurve = tc, planApi=PlanApi.FD_Api)
#gsg.planner.searchEngine = "astar(ff())"#'ehc(cea(), max_time = 30)'
#gsg.planner.updateParams()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(issaved grandma) (issaved redcap) (isdead bigbadwolf) (wellwished grandma)")

plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan)))
print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(issaved grandma) (isdead bigbadwolf) (inside  redcap bigbadwolf)")
plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan)))

print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(isdead bigbadwolf) (not (issick grandma))")

plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan)))
print()
t1 = time.time()

stories = gsg.gene_story(maxGenerations=200, acceptanceCriteria= 0.01, noS= 4, noC=40, maxDNALength=10, masterGenes=8, breeders =20)#, normalize_critic= False)

for s in stories:
    print()
    pprint.pprint(s[0])
    print(s[1])
    goal = gsg.giantTortoise.makeGoalGene(s[2])
    print(goal)

t2 = time.time()

t = t2 - t1

print(f"\nin {t} seconds")

"""
"""


"""

searchEngines = [
                "astar",
                #"eager",
                "eager_greedy",
                "eager_wastar",
                "ehc",
                "lazy",
                "lazy_greedy",  
                "lazy_wastar",
                ]

heuristics = [
                "add",
                #"blind",
                "cea",
                "cg",
                "ff",
                #"goalcount",
                "hm",
                #"hmax",
                "lmcount",

                #"const",
                "g",
                "max",
                "pref",
                "sum",
                "weight",
]

def e_const(e,h):
    return e + "(" + h + "(), max_time = 30)"


engineCheck = []
i = 0
for se in searchEngines:
    for he in heuristics:
        print(i)
        engine = e_const(se,he)

        gsg.planner.searchEngine = engine
        gsg.planner.updateParams()
        t1 = time.time()
        plan = gsg.run_planner()
        t = time.time() - t1
        score = gsg.critic_holder(PDDLAccessor.plan_splitter(plan))
        print((engine, score,t))

        if score < 2:
            engineCheck.append((engine, score,t))

        i += 1

pprint.pprint(engineCheck)

"""