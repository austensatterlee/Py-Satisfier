from CSP import CSP

def run_coin_problem():
    """ Figure out how to make 0-99 cents in change (using quarters, dimes, nickels, and pennies) """

    # Define variables
    variables = [
            ('Q',[0,1,2,3]),
            ('D',[0,1,2]),
            ('N',[0,1]),
            ('P',[0,1,2,3,4])
            ]

    # Generate constraints
    constraints=[]
    def make_constraint(n):
        return lambda Q,D,N,P:(Q*25+D*10+N*5+P==n)
    for i in xrange(100):
        constraints.append( (['Q','D','N','P'],make_constraint(i)) )

    # Solve each constraint separately and print solutions
    cprob = CSP(variables)
    for i,con in enumerate(constraints):
        cprob.reset_constraints([con])
        sol = cprob.backtrack()
        print "{0:2} cents: {1[Q]:2} quarters, {1[D]:2} dimes, {1[N]:2} nickels, {1[P]:2} pennies".format(i,sol)

def run_gui_problem():
    """ Determine the layout of some GUI elements """

    # Define variables
    variables = [
            ('th', [20,]),
            ('iph', [16,]),
            ('ip0y', range(0,100)),
            ('ip1y', range(0,100)),
            ('op0y', range(0,100))
            ]

    # Generate constraints
    constraints = []
    constraints.append( (('ip0y', 'iph'), lambda ip0y, iph: ip0y>=iph) )
    constraints.append( (('ip1y', 'ip0y', 'iph'), lambda ip1y, ip0y, iph: ip1y>=ip0y+iph) )
    constraints.append( (('op0y', 'ip0y'), lambda op0y, ip0y: op0y==ip0y) )

    cprob = CSP(variables, constraints)
    sol = cprob.backtrack()
    print sol

if __name__=="__main__":
    run_coin_problem()
    run_gui_problem()
