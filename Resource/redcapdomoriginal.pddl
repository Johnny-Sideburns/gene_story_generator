;Header and description
(define (domain fairy_tale_dom)
;remove requirements that are not needed
(:requirements :typing :conditional-effects :negative-preconditions :strips :disjunctive-preconditions :equality :action-costs)
(:types ;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
    character item location pred - omni
    agent - character
    consumable weapon - item
)
; un-comment following line if constants are needed
(:predicates ;todo: define predicates here
    (inventory ?item - item ?char - character)
    (whereabouts ?loc - location ?char - character)
    (atloc ?o - omni ?loc - location)
    (isdead ?char - character)
    (isasleep ?char - character)
    (mk_goal_single ?p - pred ?o - omni)
    (mk_goal_double ?p - pred ?o1 ?o2 - omni ?char - character)
)
(:functions ;todo: define numeric functions here
    (total-cost)
)
;define actions here
(:action move
    :parameters (?char - agent ?from ?to ?by - location)
    :precondition (and (whereabouts ?from ?char) (or (and (= ?to ?by) (atloc ?from ?to)) (and (= ?from ?by) (atloc ?to ?from))))
    :effect (and (not (whereabouts ?from ?char)) (whereabouts ?to ?char)
    (increase (total-cost) 1)
    )
)
(:action pick_up
    :parameters (?char - agent ?item - item ?loc - location)
    :precondition (and (whereabouts ?loc ?char) (atloc ?item ?loc))
    :effect (and (not (atloc ?item ?loc)) (inventory ?item ?char)
    (increase (total-cost) 1))
)
(:action drop
    :parameters (?char - agent ?item - item ?loc - location)
    :precondition (and (whereabouts ?loc ?char) (inventory ?item ?char))
    :effect (and (not (inventory ?item ?char)) (atloc ?item ?loc)
    (increase (total-cost) 1))
)
(:action give
    :parameters (?char1 - agent ?char2 - character ?item - item ?loc - location)
    :precondition (and (whereabouts ?loc ?char1) (whereabouts ?loc ?char2) (inventory ?item ?char1))
    :effect (and (not (inventory ?item ?char1)) (inventory ?item ?char2)
    (increase (total-cost) 1))
)
(:action kill
    :parameters (?char - agent ?vict - character ?wep - weapon ?loc - location)
    :precondition (and (whereabouts ?loc ?char) (whereabouts ?loc ?vict) (inventory ?wep ?char))
    :effect (and (isdead ?vict)
    (increase (total-cost) 1))
)
(:action take
    :parameters (?char1 - agent ?char2 - character ?item - item ?loc - location)
    :precondition (and (whereabouts ?loc ?char1) (whereabouts ?loc ?char2) (inventory ?item ?char2) (or (isdead ?char2) (isasleep ?char2)))
    :effect (and (not (inventory ?item ?char2)) (inventory ?item ?char1)
    (increase (total-cost) 1))
)
(:action wt_for_sleep
    :parameters (?char1 - agent ?char2 - character ?loc - location)
    :precondition (and (whereabouts ?loc ?char1) (not (whereabouts ?loc ?char2)))
    :effect (and (isasleep ?char2)
    (increase (total-cost) 1))
)
(:action tell_double
    :parameters (?char1 - agent ?char2 - character ?loc - location ?p - pred ?o1 ?o2 - omni)
    :precondition (and (whereabouts ?loc ?char1) (whereabouts ?loc ?char2))
    :effect (and (mk_goal_double ?p ?o1 ?o2 ?char2)
    (increase (total-cost) 1))
)
)