"""
auth: Jakob Ehlers
This is a script for running the gene story generator it contains addresses for different datasets and a couple of different tension curves
Simply un-comment stuff that you don't want to run

IMPORTANT!:
    in order to run with fast downward it must be installed in the same parent directory as the genestory generator,
    otherwise it is recommended to use the cloud planner, however in current version it is publically hosted,
    so sending too many requests might be considered bad form.

enjoy.
"""
import GeneStoryGenerator
import PlanApi
import time
import PDDLAccessor
import pprint


#This is a tiny example of running a pddl with the api
exampledom = "tmp/exampledom.pddl"
exampleprop = "tmp/exampleprop.pddl"

papi = PlanApi.FD_Api(exampledom,exampleprop)

plan = papi.get_plan()

print(plan)

#different data sets
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
tc5 = ([0,1,2,3,4,5,6,7,8,9],[0,1,2,3,4,5,6,4,2,0])

"""
Initiating the genestory generator
with fast downward or cloudplanner(default)
    or with a planner of choice as long as an api is added to the planApi
"""
gsg = GeneStoryGenerator.GeneStoryGenerator(data2, seed = '', tensionCurve = tc5)
#gsg = GeneStoryGenerator.GeneStoryGenerator(data2, seed = '', tensionCurve = tc5, planApi=PlanApi.FD_Api)

#example of applying a specific goal
goal1 = "(isdead bigbadwolf) (inventory flowers grandma) (issaved redcap)"
gsg.custom_problem(gsg.world,gsg.tmpProp, goal1)
plan = gsg.run_planner()

#and printing the plan with two different ways of comparing the curves
print(plan)
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='both'))
print(gsg.critic_holder(PDDLAccessor.plan_splitter(plan),normalize='relative'))
print()

t1 = time.time()
#running the gene story generator
stories = gsg.gene_story(initial = 50, maxGenerations= 100, acceptanceCriteria= 0.007, noS= 3, noC=75, maxDNALength=10, masterGenes=10, breeders = 30, normalizeCritic='both',printit = True)

stories = stories[0][:5]
stories.reverse()

#and printing the stories and grades
for s in stories:
    print()
    pprint.pprint(s[0])
    print(s[1])

t2 = time.time()

t = t2 - t1

print(f"in {t} secconds")