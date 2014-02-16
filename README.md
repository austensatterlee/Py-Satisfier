# Py-Satisfier

#### Py-Satisfier is a general CSP solver (for unary/binary constraints).

##### Defining the problem
Constraint satisfaction problems are defined with a list of variable names and associated domains. Constraints can be defined with a simple string notation. For example, given a CSP that includes two variables named *A* and *B*:
    "A>B"
Alternatively, the constraint can be defined programatically using a tuple:
    ("A",">","B")
More complicated constraints can be imposed by composing functions that build upon the binary constraint structure.
A simple example is the "AllDiff" constraint:

    def impose_alldiff(csp):
        for var1 in csp.variables:
            for var2 in csp.variables:
                if var1!=var2:
                    csp.add_constraint("%s%s%s"%(var1,CSyms.neq,var2))
        return csp

##### Finding a solution
The CSP can then be passed to a solver, such as the *backtracking* solver. This is a modular search algorithm that accepts three functions as arguments:
 * Variable selection function
    - Given the current position in the search tree, determines which variable to assign next.
 * Domain ordering function
    - Determines which values the solver will try to assign first.
 * Inference function
    - Allows the solver to impose certain consistencies on the current assignment, pruning the search tree in some cases.

