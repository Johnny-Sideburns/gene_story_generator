"""
Methods for manipulating a "world" in the form of a dictx
Auth: Jakob Ehlers
"""
import random
from IntermediateParser import *
import json

#takes: dictionary of dictionaries world,string name,string type
#returns: a dictionary entry from the world with the corresponding name
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
#takes: dictionary of dictionaries world,string name
#returns: a dictionary entry from the world with the corresponding name
def get_t(w, n):
    for t in w:
        for thing in w[t]:
            if thing['name'] == n:
                return t
    return False

#takes: dicitionary of dictionaries world
#returns: a random dictionary entry from the world
def rnd_t(w):
    l = list(w.keys())
    return random.choices(l)[0]

#takes: dicitionary of dictionaries world, string type
#returns: a random dictionary entry from the world of the corresponding type
def rnd_n(w, t):
    i = random.choices(w[t])
    n = i[0]["name"]
    return n

#takes: dicitionary of dictionaries world, string name
#returns: a dictionary entry from the world, of entries that are refferencing that name within their "predicates"
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

#takes: dicitionary of dictionaries world, dicitionary lex containing the precondition to check
#it then uses the intermediateParser to check for weather the precondition is vallid
#returns: a tupple of the result as a bool and a list of reasons why the check failed
def check_precondition(world, lex):
    acc = []
    result = True
    if type(lex) is str:
        return (False, lex)

    acc = applyFunction(lex["precondition"], lex, prec_check_shell, world,acc,andOp)
    wrongs = []
    for a in acc:
        result = result and a[0]
        if a[1] != '':
            wrongs.append(a[1])

    return (result, wrongs)

#takes: dicitionary of dictionaries world, dicitionary lex containing the action to apply
#it then uses the intermediateParser to apply the action to the world
#returns: a result as a bool of weather the check succeded
def apply_action_to_world(world, lex):
    if check_precondition(world, lex)[0]:
        applyFunction(lex["effect"], lex, apply_action_to_world_shell, world, world, andOp)
        return True
    return False

#function to be used by check_precondtion to feed the intermediateParser as the operating function to apply; to check wether the precondition is met
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

#outer function of prec_check
def prec_check_shell(expression, lex, operator, world, acc):
    operator(prec_check(world, expression, lex), acc)

#outer function of action_world
def apply_action_to_world_shell(expression, lex, operator, world, acc):
    remove = operator is notOp
    action_world(world, expression, lex, remove)
    #print(e)

def quantify_expr_vars(expr, lex):
    for y in expr.split():
        if y in lex['vars']:
            expr = expr.replace(y, lex['vars'][y][0])
    return expr

#function to be used by apply action to world to feed the intermediateParser as the operating function to apply; to check wether the precondition is met
def action_world(world, effect, lex, remove):
    effect = quantify_expr_vars(effect, lex)

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

#load open a json file
def open_world(world):        
    result = json.load(open(world))
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

#merges two dicts of dicts aka. worlds
def merge_worlds(acc,nw):
    for t in nw:
        if t not in acc:
            acc.update(t)
        else:
            for thing in nw[t]:
                if thing not in acc[t]:
                    acc[t].append(thing)


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