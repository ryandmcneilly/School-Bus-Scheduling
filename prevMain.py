import gurobipy as gp
from util.util import *
import time

EPS = 1e-10

# Sets & Data
N, N_0, N_FINAL, N_ALL, K, E, P, D, DELTA_MINUS, DELTA_PLUS, WINDOW, SCHOOL_POSITIONS = read_file(FILE_NUMBER)

M_0 = 0
M = 1000

# Lets see how long this takes!
startTime = time.time()

m = gp.Model("Heterogenous Bus Problem")
# Variables
X = {(i, j, k): m.addVar(vtype=gp.GRB.BINARY) for i in N_0 for j in N_FINAL for k in K}     # Bool to do trip
W = {(i, k): m.addVar() for i in N_0 for k in K}                                            # Service start time for bus k

# Objective
m.setObjective(gp.quicksum(((P[i] if i > 0 else 0) + D[i, j]) * X[i, j, k] for i, j, k in X) + M_0 * gp.quicksum(X[0, j, k] for k in K for j in N_FINAL), gp.GRB.MINIMIZE)

# Constraints
TripDoneWithValidBus = {j: 
    m.addConstr(gp.quicksum(E[j, k] * X[i, j, k] for k in K for i in DELTA_MINUS[j]) == 1) 
    for j in N
}

FlowBalance = {(j, k): 
    m.addConstr(gp.quicksum(X[i, j, k] for i in DELTA_MINUS[j]) == gp.quicksum(X[j, i, k] 
    for i in DELTA_PLUS[j])) for j in N for k in K
}

EnoughTime = {(i, j, k): 
    m.addConstr(W[i, k] + P[i] + D[i, j] - W[j, k] <= (1 - X[i, j, k]) * M )
    for i in N for j in N for k in K
}

InTimeWindowLess = {(j, k): 
    m.addConstr((WINDOW[j][SCHOOL_START_TIME] - P[j]) * gp.quicksum(X[i, j, k] for i in DELTA_MINUS[j]) <= W[j, k])
    for j in N for k in K
}

InTimeWindowMore = {(j, k): 
    m.addConstr((WINDOW[j][SCHOOL_END_TIME] - P[j]) * gp.quicksum(X[i, j, k] for i in DELTA_MINUS[j]) >= W[j, k])
    for j in N for k in K
}

StartAtDepot = {k: 
    m.addConstr(gp.quicksum(X[0, j, k] for j in N_FINAL) == 1) 
    for k in K
}

EndAtDepot = {k: 
    m.addConstr(gp.quicksum(X[i, len(N) + 1, k] for i in N_0) == 1) 
    for k in K
}


m.optimize()

endTime = time.time()
print(f"Model solved in {(endTime - startTime):.2f}s")


# Print out results.
if m.Status != gp.GRB.INFEASIBLE:
    num_busses = sum(round(X[i,j,k].x) for (i,j,k) in X if i==0)
    distancee = sum(P[i] + D[i, j] for (i,j,k) in X if round(X[i,j,k].x)==1)
    print("Number of busses: ", num_busses)
    print("Distance: ", distancee)
else:
    m.computeIIS()
    m.write("iismodel.ilp")
    print("-----------------------------------")
    print("EnoughTime: ")
    for i, j, k in EnoughTime:
        if EnoughTime[i, j, k].IISConstr:
            print(f"EnoughTime[{i}, {j}, {k}] is{' NOT' if not EnoughTime[i, j, k].IISConstr else ''} in the IIS")
    print("-----------------------------------")
    print("TripDonwWithValidBus: ")
    for j in TripDoneWithValidBus:
        if TripDoneWithValidBus[j].IISConstr:
            print(f"TripDonwWithValidBus[{j}] is{' NOT' if not TripDoneWithValidBus[j].IISConstr else ''} in the IIS")
    
    print("-----------------------------------")
    print("Flow Balance: ")
    for j, k in FlowBalance:
        if FlowBalance[j, k].IISConstr:
            print(f"FlowBalance[{j, k}] is{' NOT' if not FlowBalance[j, k].IISConstr else ''} in the IIS")

    for constr in [StartAtDepot, EndAtDepot]:
        print("-----------------------------------")
        print(f'{constr=}'.split('=')[0])
        for k in constr:
            if constr[k].IISConstr:
                print(f"{constr.__name__}[{k}] is{' NOT' if not constr[k].IISConstr else ''} in the IIS")

# change gurobi parameter and take average

