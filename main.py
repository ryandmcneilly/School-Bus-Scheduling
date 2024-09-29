import gurobipy as gp
from util.util import *

FILE_NUMBER = 5

# Sets & Data
N, N_0, N_FINAL, N_ALL, K, E, P, D, DELTA_MINUS, DELTA_PLUS, WINDOW = read_file(FILE_NUMBER)

M_0 = 1 << 20 - 1
M = 1 << 32 - 1

m = gp.Model("Heterogenous Bus Problem")

# Variables
X = {(i, j, k): m.addVar(vtype=gp.GRB.BINARY) for i in N_0 for j in N_FINAL for k in K}
W = {(i, k): m.addVar() for i in N_0 for k in K}

# Objective
m.setObjective(gp.quicksum(D[i, j] * X[i, j, k] for i, j, k in X) + M_0 * gp.quicksum(X[0, j, k] for k in K for j in N_FINAL), gp.GRB.MINIMIZE)

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
    m.addConstr((WINDOW[j][0] - P[j]) * gp.quicksum(X[i, j, k] for i in DELTA_MINUS[j]) <= W[j, k])
    for j in N for k in K
}

InTimeWindowMore = {(j, k): 
    m.addConstr((WINDOW[j][1] - P[j]) * gp.quicksum(X[i, j, k] for i in DELTA_MINUS[j]) <= W[j, k])
    for j in N for k in K
}

StartAtDepot = {k: 
    m.addConstr(gp.quicksum(X[0, j, k] for j in N) == 1) 
    for k in K
}

StartAtDepot = {k: 
    m.addConstr(gp.quicksum(X[i, len(N) + 1, k] for i in N) == 1) 
    for k in K
}

# 2 continuous variables for each node which are fractional which add up to the 
# Want variable with Z[i, j] which bounds with earliest starting time and latest starting timez


m.optimize()

# Print out results.
for (i, j, k) in X:
    if X[i, j, k].x > 0:
        print(f"Going from stop {i} -> {j} with bus {k} at time {W[i, k].x}")
