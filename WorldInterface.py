"""
Methods for manipulating a "world" in the form of a dictx
Auth: Jakob Ehlers
"""
import random
from IntermediateParser import *
import json

def get_smth(w,n,t = ''):
    if t == '':
        for x in w:
            result = get_smth(w,n,x)
            if result != False:
                return result
    elif t in w:
        for m in w[t]:
            if m["name"].lower() == n.lower():
                return m
    return False

def get_t(w, n):
    for t in w:
        for thing in w[t]:
            if thing['name'] == n:
                return t
    return False

def rnd_t(w):
    l = list(w.keys())
    return random.choices(l)[0]

def rnd_n(w, t):
    i = random.choices(w[t])
    n = i[0]["name"]
    return n

def find_holders(w,n):
    result = {}
    for t in w:
        for c in w[t]:
            for p in c["predicates"]:
                for name in c["predicates"][p]:
                    if name == n:
                        if t in result:
                            result[t].append(c)
                        else:
                            result.update({t:[c]})
    return result

def check_precondition(world, lex):
    acc = []
    result = True
    if type(lex) is str:
        return (False, lex)

    acc = applyFunction(lex["precondition"], lex, prec_check_shell, world,acc,andOp)
    #print(f'final {acc}')
    #pprint.pprint(lex)
    wrongs = []
    for a in acc:
        result = result and a[0]
        if a[1] != '':
            wrongs.append(a[1])
    #acc.reverse()
    
    """
    for n in range(len(acc)):
        if not acc[n]:
            tmp = lex["precondition"]['and'][n]
            tmp = 'precondtion: ' + quantify_expr_vars(tmp, lex) + ' has not been met'
            wrongs.append(tmp)
    """
    return (result, wrongs)

def apply_action_to_world(world, lex):
    if check_precondition(world, lex)[0]:
        applyFunction(lex["effect"], lex, apply_action_to_world_shell, world, world, andOp)
        return True
    #print('precondCheck failed')
    return False

def prec_check(world, precondition, lex):
    result = True
    precondition = quantify_expr_vars(precondition, lex)
    precond = precondition.split()
    prec = precond.pop(0)
    name = precond.pop()
    #if only two vars in expr, eq is assumed... for now
    if len(precond) == 0:
        if name == prec:
            return (True, '')
        else:
            return (False, f'{name} and {prec} are different')

    smth = get_smth(world, name)

    if prec in smth['predicates']:
        for p in precond:
            result = result and (p in smth['predicates'][prec])
    
    if result:
        return (result, '')
    return (result, 'precondition ' + precondition + ' has not been satisfied')

def prec_check_shell(expression, lex, operator, world, acc):
    operator(prec_check(world, expression, lex), acc)
    """
    if pc != None:
        if type(acc) is list:
            return acc.append(pc)
        return pc
    """

def apply_action_to_world_shell(expression, lex, operator, world, acc):
    remove = operator is notOp
    action_world(world, expression, lex, remove)
    #print(e)

def quantify_expr_vars(expr, lex):
    for y in expr.split():
        if y in lex['vars']:
            expr = expr.replace(y, lex['vars'][y][0])
    return expr

def action_world(world, effect, lex, remove):
    effect = quantify_expr_vars(effect, lex)

    #print(effect)
    effe = effect.split()
    #ignoring func for now
    if len(effe) < 2:
        return
    pred = effe.pop(0)
    name = effe.pop()

    smth = get_smth(world, name)

    if pred in smth['predicates']:
        for p in effe:
            if remove:
                smth['predicates'][pred].remove(p)
            else:
                smth['predicates'][pred].append(p)
    elif effe == []:
        smth['predicates'][pred] = ['']
    else:
        smth['predicates'][pred] = effe
    return smth

def open_world(world):        
    result = json.load(open(world))
    return result

def mk_agent(world, agent):
    if agent in world['- character']:
        world['- character'].remove(agent)
    world["- agent"] = [agent]

def pop_character(world, character = ''):
    if (character == ''):
        n = random.randint(0, len(world["- character"]) -1)
        return world["- character"].pop(n)

def get_character(world, character = ''):
    if (character == ''):
        n = random.randint(0, len(world["- character"]) -1)
        return world["- character"][n]

#takes in a character dict and turns predicate abstracted goals into goals
#currently only applied to mk_goal_double
def formulate_goal(char):
    if 'mk_goal_double' in char['predicates']:
        if 'goals' not in char:
            char['goals'] = []
        #formulates "mk_goal_double"'s into comprehensive goals
        while(len(char['predicates']['mk_goal_double']) > 1):
            tmpgoal = []
            #a mk_goal_double contains three pieces of information; predicate and two vars,
            for n in range(3):
                tmpgoal.append(char['predicates']['mk_goal_double'].pop(0))
            goal = mk_goal_double(tmpgoal)
            if goal not in char['goals']:
                char['goals'].append(goal)
        purge_thing_if_empty(char['predicates'], 'mk_goal_double')

#takes an ordered list of (str) pddl types and turns them into a goal string
def mk_goal_double(goal):
    result = '('
    result = result + goal.pop(0)
    for n in range(len(goal)):
        result = result + ' ' + goal[n]
    result = result + ')'
    return result

#recursively adds types from world, associated to character, to accumulator
def add_associations(world, character, acc):
    for p in character["predicates"]:
        for n in character["predicates"][p]:
            for t in world:
                x = get_smth(world,n,t)
                if x:
                    if t in acc:
                        acc[t].append(x)
                    else:
                        acc.update({t : [x]})
                    add_associations(world,x,acc)

def merge_worlds(acc,nw):
    for t in nw:
        if t not in acc:
            acc.update(t)
        else:
            for thing in nw[t]:
                if thing not in acc[t]:
                    acc[t].append(thing)
        
def get_impending_plan_steps(world, blackList = []):
    result = []
    for c in world["- character"]:
        if c['name'] in blackList:
            #print(f"{c['name']} is blacklisted")
            pass
        elif 'plan' in c and len(c['plan']) > 0:
            p = c['plan'][0]
            result.append((c['name'], p))
    return result

def remove_item_from_thing(char, thing, item):
    if thing in char:
        if item in char[thing]:
            char[thing].remove(item)
            purge_thing_if_empty(char, thing)

def purge_thing_if_empty(holder, thing):
    if thing in holder:
        if len(holder[thing]) == 0:
            del holder[thing]


"""
testing stuff

import json
wld = json.load(open("tmp/world.json"))

ty = rnd_t(wld)
#print(ty)
nm = rnd_n(wld,ty)
#print(nm)
smt = get_smth(wld,ty,nm)
print(smt)
"""
"""
redacted code

def check_precondition_rec(world, precond, lex, acc, nut = False):
    for p in precond:
        if (p == 'and'):
            for x in precond[p]:
                check_precondition_rec(world, x, lex, acc)
        elif (p == 'not'):
            check_precondition_rec(world, precond[p], lex, acc, True)
        elif (p == 'or'):
            tmp = []
            for x in precond[p]:
                check_precondition_rec(world, x, lex, tmp)
            a = False
            for t in tmp:
                if (t):
                    a = t
                    break
            acc.append(a)

        else:
            if nut: 
                return acc.append(not prec_check(world, precond, lex))
            return acc.append(prec_check(world, precond, lex))

"""
