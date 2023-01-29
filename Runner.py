import GeneStoryGenerator
import PlanApi
import pprint
import time


dom = "Resource/redcapdomExpanded.pddl"
world = "Resource/redCapWorldExpanded.json"

l1 = "Resource/RedRidingLex.json"

data = (world,dom,l1)

gsg = GeneStoryGenerator.GeneStoryGenerator(data, planApi=PlanApi.FD_Api, seed = '', tensionCurve = ([0,1,2,3,4,5,6,7],[0,1,2,4,6,5,2.5,0]))

gsg.custom_problem(gsg.world,gsg.tmpProp,"(issaved grandma) (issaved redcap)")#, metric="(:metric minimize (total-cost))\n")

plan = gsg.run_planner()

print(plan)
print()

gsg.custom_problem(gsg.world,gsg.tmpProp,"(isdead bigbadwolf) (not (issick grandma))", metric="(:metric minimize (total-cost))\n")

plan = gsg.run_planner()

print(plan)
print()

t1 = time.time()

stories = gsg.gene_story(maxGenerations=150, acceptanceCriteria= 0.0001, noS= 2, noC=20, maxDNALength=10)#, normalize_critic= False)

for s in stories:
    print()
    pprint.pprint(s[0])
    print(s[1])

t2 = time.time()

t = t2 - t1

print(f"\nin {time} seconds")