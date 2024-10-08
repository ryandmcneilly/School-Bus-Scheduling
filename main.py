import gurobipy as gp
from util.util import *

FILE_NUMBER = 10
EPS = 1e-3

# Sets & Data
N, N_0, N_FINAL, N_ALL, K, E, P, D, DELTA_MINUS, DELTA_PLUS, WINDOW, SCHOOL_POSITIONS = read_file(FILE_NUMBER)



m = gp.Model("Heterogenous Bus Problem")

# Variables
X = {(i, j, k): m.addVar() for i in N_0 for j in N_FINAL for k in K}     # Bool to do trip
Z = {(i, j, mode): m.addVar() for i in N_0 for j in N_FINAL for mode in (EARLY, LATE)}      # Bounding variable times

# Objective
m.setObjective(gp.quicksum(((P[i] if i > 0 else 0) + D[i, j]) * X[i, j, k] for i in N_0 for j in N for k in K) + M_0 * gp.quicksum(X[0, j, k] for k in K for j in N_FINAL), gp.GRB.MINIMIZE)

# Constraints
TripDoneWithValidBus = {j: 
    m.addConstr(gp.quicksum(E[j, k] * X[i, j, k] for k in K for i in DELTA_MINUS[j]) == 1) 
    for j in N
}

FlowBalance = {(j, k): 
    m.addConstr(gp.quicksum(X[i, j, k] for i in DELTA_MINUS[j]) == gp.quicksum(X[j, i, k] 
    for i in DELTA_PLUS[j])) for j in N for k in K
}

TimeWindowBound = {(i): m.addConstr(
    gp.quicksum(
        Z[i, j, EARLY] * WINDOW[i][SCHOOL_START_TIME] + 
        Z[i, j, LATE] * (WINDOW[j][SCHOOL_END_TIME] - P[i] - D[i, j]) for j in N
    ) >= gp.quicksum(
        Z[j, i, EARLY] * (WINDOW[j][SCHOOL_START_TIME]) + 
        Z[j, i, LATE] * WINDOW[i][SCHOOL_END_TIME] - P[j] + D[j, i] for j in N))
    for i in N
}

FractionalBoundSum = {(i, j): 
    m.addConstr(Z[i, j, EARLY] + Z[i, j, LATE] == gp.quicksum(X[i, j, k] for k in K)) 
    for i in N for j in N
}


StartAtDepot = {k: 
    m.addConstr(gp.quicksum(X[0, j, k] for j in DELTA_PLUS[0]) == 1) 
    for k in K
}

EndAtDepot = {k: 
    m.addConstr(gp.quicksum(X[i, len(N) + 1, k] for i in DELTA_MINUS[len(N) + 1]) == 1) 
    for k in K
}

m.optimize()


# Print out results.
if m.Status != gp.GRB.INFEASIBLE:
    num_busses = len([1 for k in K if len([1 for j in N_FINAL if X[0, j, k].x > 0])> 0 ]  )
    distancee = sum([(P[i] if i > 0 else 0) + D[i, j] for (i, j, k) in X if X[i, j, k].x > 0])
    print("Number of busses: ", num_busses)
    print("Distance: ", distancee)
else:
    m.computeIIS()
    m.write("iismodel.ilp")
    
    print("-----------------------------------")
    print("TripDoneWithValidBus: ")
    for j in TripDoneWithValidBus:
        if TripDoneWithValidBus[j].IISConstr:
            print(f"TripDoneWithValidBus[{j}] is{' NOT' if not TripDoneWithValidBus[j].IISConstr else ''} in the IIS")
    
    print("-----------------------------------")
    print("Flow Balance: ")
    for j, k in FlowBalance:
        if FlowBalance[j, k].IISConstr:
            print(f"FlowBalance[{j, k}] is{' NOT' if not FlowBalance[j, k].IISConstr else ''} in the IIS")

    print('----------------------------------')
    print("TimeWindowBound: ")
    for i in TimeWindowBound:
        if TimeWindowBound[i].IISConstr:
            print(f"TimeWindowBound[{i}] is{' NOT' if not TimeWindowBound[i].IISConstr else ''} in the IIS")

    print('----------------------------------')
    print("FractionalBoundSum: ")
    for i, j in FractionalBoundSum:
        if FractionalBoundSum[i, j].IISConstr:
            # print(f"FractionalBoundSum[{i, j}] is in the IIS")
            pass

    print('----------------------------------')
    