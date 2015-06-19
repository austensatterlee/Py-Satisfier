import sys
import copy as cp
from heuristics import *

class CSP(object):
    """Constraint problem definition"""
    def __init__(self,variables=None,constraints=None):
        """
        Create a new constraint satisfaction problem.

        Keyword arguments:
        variables - a list of `variables`.
        constraints - a list of `constraints`.

        A `variable` is a pairing (variable name, list of valid
        assignments), e.g.: ('boolvar1', [0,1]).
        A `constraint` is a paring (relevant variables, constraint
        function), e.g. (('x1','x2'),lambda x1,x2:x1!=x2).

        """
        self.variables = []
        self.domains = {}
        self.constraints = []
        self.arcs = {}
        if variables:
            for variable in variables:
                self.add_variable(*variable)
        if constraints:
            for constraint in constraints:
                self.add_constraint(*constraint)
    def __str__(self):
        mystr = '\n'.join(['{}: {}'.format(v,self.domains[v]) for v in self.variables])
        mystr += '\n'.join(map(str,self.constraints))
        return mystr
    def clone(self):
        return cp.deepcopy(self)
    def add_variables(self,*args):
        """
        Define variables relevant to the problem

        Parameters are specified as follows:
        --
        add_variables('var1',domain1,'var2',domain2,...)
        -OR-
        add_variables(['var1','var2',...],domain)
        Note that in the second usage the same domain is used for each variable.

        """
        if len(args)%2!=0:
            raise ValueError('Arguments should be given in pairs (see doctype)')
        if type(args[0])!=str:
            variables,domain=args
            for var in variables:
                self.add_variable(var,domain)
        else:
            for i in xrange(0,len(args),2):
                var,domain = args[i],args[i+1]
                self.add_variable(var,domain)
    def add_variable(self,varname,domain):
        """Add a new variable to the constraint graph."""
        if varname in self.variables:
            raise ValueError("Variable already in constraint graph")
        else:
            self.variables.append(varname)
            self.domains[varname] = domain
            self.arcs[varname] = {}
    def add_constraint(self,varnames,func):
        """
        Impose a constraint.

        Arguments:
        varnames   -   Names of the variables involved in the constraint
        func       -   Constraint evaluation function (argument order should match variables parameter)

        """
        constraint = (varnames,func)
        for var1 in varnames:
            for var2 in varnames:
                if var1==var2:
                    continue
                if var2 not in self.arcs[var1]:
                    self.arcs[var1][var2] = []
                self.arcs[var1][var2].append(constraint)
        self.constraints.append(constraint)
    def reset_constraints(self,constraints=[]):
        """
        Impose a list of constraints and remove any previous constraints from the problem.

        """
        self.constraints = []
        for varname in self.arcs:
            self.arcs[varname]={}
        for constraint in constraints:
            self.add_constraint(*constraint)
    def check_constraints(self,assignment,constraints=None):
        """
        Verify an assignment against specified constraints.

        Arguments:
        assignment  -   Dictionary specifying assignments of some variables in the CSP.
        constraints -   List of constraints to test against. 
                        (Defaults to all constraints in the CSP.)

        Returns: True if the assignment violates no constraints.
        """
        result = True
        if constraints==None:
            constraints = self.constraints
        for constraint in constraints:
            result = result and self.check_constraint(assignment,constraint)
        return result
    def check_constraint(self,assignment,constraint):
        """Verify an assignment against a single constraint""" 
        varnames,func = constraint
        values = []
        for varname in varnames:
            if varname not in assignment:
                return True
            else:
                values.append(assignment[varname])
        return func(*values)
    def get_arcs(self,variables=None):
        """
        Return all constraint pairs involving the specified variables.
        If no variables are specified, all pairs are returned.
        """
        arcs = []

        if variables==None:
            variables = self.arcs
        for tail in variables:
            if not self.arcs[tail]:
                continue
            for head in self.arcs[tail]:
                if (tail,head) not in arcs:
                    arcs.append((tail,head))
        return arcs
    def ensure_arc_consistent(self,arcs=None):
        """
        Returns an arc consistent copy of this CSP
        If arcs are provided, only those arcs are checked.

        """
        def revise(csp,tail_var,head_var):
            """
            Prunes domain of the tail variable to ensure arc consistency.

            Returns: True iff tail variable's domain was revised
            """
            assignment = {tail_var:None,head_var:None}
            arc_constraints = csp.arcs[tail_var][head_var]
            revised = False
            tail_domain = csp.domains[tail_var][:]
            for tail_val in tail_domain:
                assignment[tail_var]=tail_val
                needs_revision = True
                for head_val in csp.domains[head_var]:
                    assignment[head_var]=head_val
                    if csp.check_constraints(assignment,arc_constraints):
                        needs_revision = False
                        break
                if needs_revision:
                    csp.domains[tail_var].remove(tail_val)
                    revised = True
            return revised

        new_csp = self.clone()
        propagate = True
        if arcs==None:
            arc_queue = new_csp.get_arcs()
        else:
            propagate = False
            arc_queue = arcs
        while len(arc_queue)>0:
            arc = arc_queue.pop()
            tail,head = arc
            if revise(new_csp,tail,head):
                if len(new_csp.domains[tail])==0:
                    return False
                if propagate:
                    neighbors = self.get_arcs(variables=[tail])
                    for neighbor in neighbors:
                        if neighbor not in arc_queue:
                            arc_queue.append(neighbor)
        return new_csp

    def backtrack(self,sf=simple_select,of=simple_order,iff=simple_infer,ret_stats=False,verbose=0):
        """Perform backtrack search to find a solution to the CSP

        Arguments:
        sf  -   Variable selection function
        of  -   Domain ordering function
        iff  -   Inference function

        """
        csp = self
        select_func,order_func,infer_func = sf,of,iff
        assignment = {}
        search_stats = dict(visited=0)
        stack = [({},csp)]
        history = {}
        result = False
        while len(stack)>0:
            assignment,csp = stack.pop()
            assignmenthash = str([assignment.get(varname,None) for varname in self.variables])
            history[assignmenthash]=True

            search_stats['visited']+=1
            #if show_progress:
                #prog_str = "{}...{}".format(assignment,search_stats['visited'])
                #sys.stdout.write( prog_str )
                #sys.stdout.write( '\b'*len(prog_str) )
            if verbose>1:
                print assignmenthash
            if csp.check_constraints(assignment)!=False:
                if len(assignment)==len(csp.variables):
                    result = assignment
                    break
                var = select_func(assignment,csp)
                for value in order_func(var,assignment,csp):
                    newassignment = assignment.copy()
                    inferences = infer_func(csp,var,value)
                    if inferences!=False:
                        newassignment.update(inferences)
                        newassignment[var] = value
                        stack.append((newassignment,csp))
        if verbose>0:
            for stat in search_stats:
                print stat+": %d"%search_stats[stat]
        if ret_stats:
            return (result,search_stats)
        else:
            return result
