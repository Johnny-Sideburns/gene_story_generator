import GeneStoryGenerator
import PlanApi
import pprint
import time
import PDDLAccessor

dom = "Resource/redcapdomExpanded.pddl"
world = "Resource/redCapWorldExpanded.json"

l1 = "Resource/RedRidingLex.json"

data = (world,dom,l1)

tc = ([0,1,2,3,4,5,6,7],[0,1,2,3,4,5,3,1])
tc2 = ([0,4,5,8,13,14,16,17,18,19],[0,1,2,3,4,5,4,3,1,0])


gsg = GeneStoryGenerator.GeneStoryGenerator(data, seed = '', tensionCurve = tc2, planApi=PlanApi.FD_Api)
#gsg.planner.searchEngine = "astar(ff())"#'ehc(cea(), max_time = 30)'
#gsg.planner.updateParams()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(issaved grandma) (issaved redcap) (isdead bigbadwolf) (wellwished grandma)")

plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan)))
print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(isdead bigbadwolf) (not (issick grandma))")

plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan)))
print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(issaved grandma) (isdead bigbadwolf) (inside  redcap bigbadwolf)")
plan = gsg.run_planner()

print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan)))

print()



t1 = time.time()

stories = gsg.gene_story(initial = 100, maxGenerations=100, acceptanceCriteria= 0.01, noS= 4, noC=40, maxDNALength=10, masterGenes=8, breeders =20)#, normalize_critic= False)

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