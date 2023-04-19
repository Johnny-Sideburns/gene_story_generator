import GeneStoryGenerator
import PlanApi
import pprint
import time
import PDDLAccessor

exampledom = "tmp/exampledom.pddl"
exampleprop = "tmp/exampleprop.pddl"

papi = PlanApi.FD_Api(exampledom,exampleprop)

plan = papi.get_plan()

print(plan)

dom = "Resource/redcapdomExpanded.pddl"
dom1 = "Resource/redcapdom.pddl"
world = "Resource/redCapWorldExpanded.json"
world1 = "Resource/redCapWorld.json"

l1 = "Resource/RedRidingLex.json"

data = (world1,dom1,l1)

tc = ([0,1,2,3,4,5,6,7,8,9,10,11,12],[0,1,2,3,4,5,6,7,8,7,5,3,1])
tc2 = ([0,4,5,8,13,14,16,17,18,19],[0,1,2,3,4,5,4,3,1,0])
tc3 = ([0,1,2,3,4,5,6,7,8,9,10],[0,1,2,3,5,7,8,6,4,2,1])
tc4 = ([0,1,5,6,8,14,15,17,18,19,20],[0,1,2,3,5,7,8,6,4,2,1])

gsg = GeneStoryGenerator.GeneStoryGenerator(data, seed = '', tensionCurve = tc3, planApi=PlanApi.FD_Api)
#gsg.planner.searchEngine = "astar(ff())"#'ehc(cea(), max_time = 30)'
#gsg.planner.updateParams()


gsg.custom_problem(gsg.world,gsg.tmpProp,"(issaved grandma) (issaved redcap) (isdead bigbadwolf) (inventory flowers grandma)")

plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='both'))
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='no'))
"""

print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(isdead bigbadwolf) (not (issick grandma))")

plan = gsg.run_planner(True)

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='both'))
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='no'))
print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(issaved grandma) (isdead bigbadwolf) (inside  redcap bigbadwolf)")
plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='both'))
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='no'))
print()



t1 = time.time()

stories = gsg.gene_story(initial = 100, maxGenerations= 50, acceptanceCriteria= 0.007, noS= 4, noC=100, maxDNALength=10, masterGenes=10, breeders = 30)

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