import os
from pprint import pprint
import subprocess
import sys
import requests
from PDDLAccessor import *
import atexit

sys.path.append('../')


class Plan_Api:
    def __init__(self, dom, prob):
        self.dom = dom
        self.prob = prob

    def updateParams(self):
        pass

    def get_plan(self):
        pass
"""
"""
#magic from fast-downward
DRIVER_DIR = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT_DIR = os.path.dirname(DRIVER_DIR)
BUILDS_DIR = os.path.join(REPO_ROOT_DIR, "builds")

#planner = plan_manager.PlanManager('plannies')
class FD_Api(Plan_Api):
    def __init__(self, dom, prob):
        self.dom = name_extractor(dom)
        self.prob = name_extractor(prob)
        self.sasPlan = "..\sas_plan"
        self.updateParams()
        
    def updateParams(self):
        dom = "gene_story_generator\\tmp\\" + name_extractor(self.dom) + ".pddl"
        prob = "gene_story_generator\\tmp\\" + name_extractor(self.prob) + ".pddl"
        self.parameters = [
            #"downward\\misc\\tests\\benchmarks\\gripper\\domain.pddl",
            #"downward\\misc\\tests\\benchmarks\\gripper\\prob01.pddl",
            #"gene_story_generator\\tmp\\domdom.pddl",
            #"gene_story_generator\\tmp\\probcopy.pddl",
            #"--evaluator",
            #"--debug",
            
            dom,
            prob,

            "--search-options",

            #"--run all",
            "--search",
            #"--evaluator",
            #"hff=ff()", 
            #"hcea=cea()", 
            "lazy_greedy([ff(), cea()], max_time = 5, preferred=[ff(), cea()])"
            #"astar(lmcut())",
            #"astar(ff())"
            #"astar(lmcount(lm_rhw()))"
            #"astar(cegar())",
            #"--sas-file"
            #"astar(blind())"

            #"eager(epsilon_greedy(cegar()), verbosity=silent)"

            #"astar(cg(max_cache_size=1000000, transform=no_transform(), cache_estimates=true),max_time = 600)"
            #"astar(cg(max_cache_size=1000,cache_estimates=true))"
            #"merge_and_shrink(transform=no_transform(), cache_estimates=true, merge_strategy, shrink_strategy, label_reduction=<none>, prune_unreachable_states=true, prune_irrelevant_states=true, max_states=-1, max_states_before_merge=-1, threshold_before_merge=-1, verbosity=normal, main_loop_max_time=infinity)"

            #"ff(transform=no_transform(), cache_estimates=true)"

            ]

    #run driver
    def get_plan(self, show = False):
        if (os.path.exists(self.sasPlan)):
            os.remove(self.sasPlan)
        cmd = [sys.executable, "downward/fast-downward.py"] + self.parameters
        result = subprocess.run(cmd, cwd=REPO_ROOT_DIR, capture_output = not show)

        if (os.path.exists(self.sasPlan)):
            return read_file(self.sasPlan)

        else: 
            pass
            #subprocess.run(cmd, cwd=REPO_ROOT_DIR, capture_output = show)
        return ''

class Cloud_Planner_Api(Plan_Api):
    def __init__(self, dom, prob):
        super().__init__(dom, prob)
        if (dom != '' and prob != ''):
            self.updateParams()

    def updateParams(self):
        self.parameters = {
            'domain': read_file(self.dom),
            'problem': read_file(self.prob)}

    def get_plan(self, show = True):

        resp = requests.post('http://solver.planning.domains/solve', verify=False, json=self.parameters)
        """
        resp = requests.post('http://calm-everglades-35579.herokuapp.com/solve', verify=False, json=self.parameters)
        resp = requests.post('http://dry-tundra-82186.herokuapp.com/solve', verify=False, json=self.parameters)
        """
        if (resp.status_code != 200):
            result = 'Response <' + str(resp.status_code) +'>: ' + resp.reason
            #print(f'Response <{resp.status_code}>: {resp.reason}')
            #print(result)
            return result
        resp = resp.json()
        #with open("planFileNameHolder", 'w') as f:
        #    f.write('\n'.join([act['name'] for act in resp['result']['plan']]))
        if (resp['status'] == 'error'):
            if (show):
                print()
                pprint(resp)
                print()
            plan = ''
        else:
            plan = ('\n'.join([act['name'] for act in resp['result']['plan']]))
            if(show):
                #pprint(resp['result']['output'])
                pprint(resp)
        #print(plan)
        
        return plan

def read_file(fileName):
    openedFile = open(fileName)
    result = openedFile.read()
    openedFile.close()
    return result


#rumBriber(parameters)

#lmcount(lm_factory, admissible=false, optimal=false, pref=false, alm=true, lpsolver=CPLEX, transform=no_transform(), cache_estimates=true)