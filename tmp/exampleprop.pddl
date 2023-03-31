(define (problem ex) (:domain example)
(:objects 
    dudeAscii - agent
    onePlace anotherPlace - location
)
(:init
    (atloc dudeAscii onePlace)
)

(:goal 
(and
    (atloc dudeAscii anotherPlace)
)
)
)
