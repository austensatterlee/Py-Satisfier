import heapq
import random

# Trivial heuristics and consistency functions
def simple_select(assignment,csp):
    unassigned = filter(lambda(x):not assignment.get(x,False),csp.variables)
    return random.choice(unassigned)
def simple_order(var,assignment,csp):
    return csp.domains[var]
def simple_infer(csp,var,value):
    return {}
def lcv_order(var,assignment,csp):
    neighbors = csp.get_arcs([var])
    ordering = []
    for val in csp.domains[var]:
        newcsp = csp.ensure_arc_consistent(neighbors)
        num_choices = sum(map(len,csp.domains.items()))
        ordering.append((num_choices,val))
    heapq.heapify(ordering)
    return [x[1] for x in ordering]

