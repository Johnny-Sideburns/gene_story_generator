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
dom2 = "Resource/redcapdom2.pddl"

world = "Resource/redCapWorldExpanded.json"
world1 = "Resource/redCapWorld.json"
world2 = "Resource/redCapWorld2.json"

l1 = "Resource/RedRidingLex.json"

data = (world,dom,l1)
data1 = (world1,dom1,l1)
data2 = (world2, dom2, l1)

tc = ([0,1,2,3,4,5,6,7,8,9,10,11,12],[0,1,2,3,4,5,6,7,8,7,5,3,1])
tc2 = ([0,4,5,8,13,14,16,17,18,19],[0,1,2,3,4,5,4,3,1,0])
tc3 = ([0,1,2,3,4,5,6,7,8,9,10],[0,1,2,3,5,7,8,6,4,2,1])
tc4 = ([0,1,5,6,8,14,15,17,18,19,20],[0,1,2,3,5,7,8,6,4,2,1])
tc5 = ([0,1,2,3,4,5,6,7,8,9],[0,1,2,3,4,5,6,4,2,1])

gsg = GeneStoryGenerator.GeneStoryGenerator(data2, seed = '', tensionCurve = tc5, planApi=PlanApi.FD_Api)
#gsg.planner.searchEngine = "astar(ff())"#'ehc(cea(), max_time = 30)'
#gsg.planner.updateParams()


goal1 = "(isdead bigbadwolf) (inventory flowers grandma) (issaved redcap)"
gsg.custom_problem(gsg.world,gsg.tmpProp, goal1)
plan = gsg.run_planner()
print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='both'))
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='relative'))
print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(not (issick grandma)) (isdead bigbadwolf)")

plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='both'))
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='relative'))
print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(not (issick grandma))")
plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='both'))
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='relative'))
print()
"""
"""

t1 = time.time()

stories = gsg.gene_story(initial = 50, maxGenerations= 200, acceptanceCriteria= 0.005, noS= 5, noC=75, maxDNALength=10, masterGenes=10, breeders = 30, normalizeCritic='both')

stories.reverse()


for s in stories:
    print()
    pprint.pprint(s[0])
    print(s[1])
    goal = gsg.giantTortoise.makeGoalGene(s[2])
    print(goal)

t2 = time.time()

t = t2 - t1

print(f"\nin {t} seconds")
