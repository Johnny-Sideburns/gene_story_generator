;Header and description

(define (domain example)

;remove requirements that are not needed
(:requirements :strips :typing :conditional-effects :negative-preconditions :equality)

(:types
    agent
    location
)
(:predicates
    (atloc ?a - agent ?l - location)
)
(:action move
    :parameters (?a - agent ?l1 ?l2 - location)
    :precondition (and (atloc ?a ?l1))
    :effect (and (not (atloc ?a ?l1)) (atloc ?a ?l2))
)

)