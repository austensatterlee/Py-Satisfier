import random
import re
class CSP(object):
    """Constraint graph for binary, conjuctive constraints"""
    def __init__(self,variables=None,domain=None):
        """Create a new constraint satisfaction problem."""
        self.variables = []
        self.domains = {}
        self.constraints = []
        self.arcs = {}
        if variables and domain:
            self.add_variables(variables,domain)
    def add_variables(self,variables,domain):
        """Adds a list of variables with the same domain to the CSP"""
        for var in variables:
            self.add_variable(var,domain)
    def add_variable(self,varname,domain):
        """Add a new variable to the constraint graph."""
        if varname in self.variables:
            raise ValueError("Variable already in constraint graph")
        else:
            self.variables.append(varname)
            self.domains[varname] = domain
            self.arcs[varname] = []
    def add_constraint(self,c_str):
        """Impose a unary or binary constraint.
        
        Arguments:
        c_str   -   constraint string, or a 3-tuple: (var1,constraint symbol,var2|val)
        
        A constraint string is a string composed of alphanumeric characters,
        including one of the constraint symbols (see CSyms class).
        The constraint symbol must be preceded by a CSP variable name,
        and succeeded by either a CSP variable name, or some value.

        """
        if type(c_str)==str:
            constraint = parse_constraint_str(c_str)
        else:
            constraint = c_str
        var1,csym,var2 = constraint
        self.constraints.append(constraint)
        self.arcs[var1].append(constraint)
        if var2 in self.variables:
            self.arcs[var2].append(constraint)
    def add_constraints(self,*constraint_strings):
        for c_str in constraint_strings:
            self.add_constraint(c_str)
    def check_constraints(self,assignment):
        result = True
        for constraint in self.constraints:
            result = result and self.check_constraint(assignment,constraint)
        return result
    def check_constraint(self,assignment,constraint):
        """
        Evaluate constraint by reducing variables into values
        and passing to the evaluator.
        
        """
        var1,c_sym,var2 = constraint
        if var1 in assignment:
            val1 = assignment[var1]
        else:
            return True

        if var2 in assignment:
            val2 = assignment[var2]
        elif var2 in self.variables:
            return True
        else:
            val2 = var2
        return eval_constraint(val1,c_sym,val2)

class Assignment(object):
    def __init__(self,csp):
        self.csp = csp
        self.domains = self.copy_domains(csp)
    def add_value(self,var,value):
        self.domains[var] = value
    def clone(self):
        c = Assignment(csp)
        c.domains = self.copy_domains(self)
    def copy_domains(self,target):
        domains_c = {}
        for var in target.domains:
            domain_c = target.domains[var][:]
            domains_c[var]=domain_c
        return domains_c

# Trivial heuristics and consistency functions
def simple_select(assignment,csp):
    unassigned = filter(lambda(x):not assignment.get(x,False),csp.variables)
    return random.choice(unassigned)
def simple_order(var,assignment,csp):
    return csp.domains[var]
def simple_infer(csp,var,value):
    return {}

def backtracking_search(csp,sf=simple_select,of=simple_order,iff=simple_infer):
    """Perform backtrack search to find a solution to the given csp.

    Arguments:
    csp -   A csp containing variables, domains, and constraints.
    sf  -   Variable selection function
    of  -   Domain ordering function
    iff  -   Inference function

    """
    select_func,order_func,infer_func = sf,of,iff
    assignment = {}
    def backtrack(assignment,csp):
        if len(assignment)==len(csp.variables):
            return assignment
        var = select_func(assignment,csp)
        for value in order_func(var,assignment,csp): 
            oldassignment = assignment.copy()
            assignment[var] = value
            if csp.check_constraints(assignment):
                inferences = infer_func(csp,var,value)
                if inferences!=False:
                    assignment.update(inferences)
                    result = backtrack(assignment,csp)
                    if result!=False:
                        return result
            assignment = oldassignment
        return False
    return backtrack(assignment,csp)


class CSyms:
    eq = '='
    neq = '!='
    gt = '>'
    gte = '>='
    lt = '<'
    lte = '<='
    as_list = filter(lambda(x):not x.startswith('_') and x!='as_list',vars(CSyms))

def parse_constraint_str(cstr):
    syms_pattern = '|'.join(map(CSyms.__dict__.get,CSyms.as_list))
    pattern = "(^.+?)(%s)(.+?$)"%syms_pattern
    split_result = re.match(pattern,cstr)
    # print pattern,'->',cstr,'=',split_result.groups()
    return split_result.groups()

def eval_constraint(val1,c_sym,val2):
    if c_sym=='==':
        return val1==val2
    elif c_sym=='!=':
        return val1!=val2
    elif c_sym=='>':
        return val1>val2
    elif c_sym=='<':
        return val1<val2
    elif c_sym=='>=':
        return val1>=val2
    elif c_sym=='<=':
        return val1<=val2
    else:
        raise ValueError("Constraint "+c_sym+" not understood")
def add_alldiff(csp):
    for var1 in csp.variables:
        for var2 in csp.variables:
            if var1==var2:
                continue
            csp.add_constraint("%s%s%s"%(var1,CSyms.neq,var2))
    return csp



