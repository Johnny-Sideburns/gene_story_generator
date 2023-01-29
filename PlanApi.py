"""
a class for acting as api for third party planners
Auth: Jakob Ehlers
"""

import os
from pprint import pprint
import subprocess
import sys
import requests
from PDDLAccessor import *

sys.path.append('../')

#parent class
class Plan_Api:
    #init takes a Pddl domain and problem file paths as strings
    def __init__(self, dom, prob):
        self.dom = dom
        self.prob = prob

    #update the parameters
    def updateParams(self):
        pass

    #run the plan and return it
    def get_plan(self):
        pass

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

            dom,
            prob,

            "--search-options",
            "--search",
            
            "lazy_greedy([ff(), cea()], max_time = 5, preferred=[ff(), cea()])"
            #"astar(lmcut())",
            #"astar(ff())"
            #"astar(lmcount(lm_rhw()))"
            #"astar(cegar())",
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
        #these two cloud solvers were hosted on heroku, but ran into a sudden case of not working caused by a monetarily motivated policy change by the host company
        """
        resp = requests.post('http://calm-everglades-35579.herokuapp.com/solve', verify=False, json=self.parameters)
        resp = requests.post('http://dry-tundra-82186.herokuapp.com/solve', verify=False, json=self.parameters)
        """
        if (resp.status_code != 200):
            result = 'Response <' + str(resp.status_code) +'>: ' + resp.reason
            return result
        resp = resp.json()

        if (resp['status'] == 'error'):
            if (show):
                print()
                pprint(resp)
                print()
            plan = ''
        else:
            plan = ('\n'.join([act['name'] for act in resp['result']['plan']]))
            if(show):
                pprint(resp)
        
        return plan

#returns a string of the contents from a filename
def read_file(fileName):
    openedFile = open(fileName)
    result = openedFile.read()
    openedFile.close()
    return result
