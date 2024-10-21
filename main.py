import gurobipy as gp
from util.util import *
import time
EPS = 1e-3

# Sets & Data
N, N_0, N_FINAL, N_ALL, T, NUM, CAP, E, P, D, DELTA_MINUS, DELTA_PLUS, WINDOW, SCHOOL_POSITIONS = read_file(FILE_NUMBER)

# Lets see how long this takes!
startTime = time.time()

m = gp.Model("Heterogenous Bus Problem")

# Variables
X = {(i, j, t): m.addVar() for i in N_0 for j in N_FINAL for t in T if E[j, t]}     # Bool to do trip
Z = {(i, j, mode): m.addVar() for i in N_0 for j in N_FINAL for mode in (EARLY, LATE)}      # Bounding variable times

# Objective
m.setObjective(gp.quicksum((P[i] + D[i, j]) * X[i, j, t] for i, j, t in X) + M_0 * gp.quicksum(X[0, j, t] for (_, j, t) in X), gp.GRB.MINIMIZE)

# Constraints
ForceZero = m.addConstr(gp.quicksum(X[i,j,t] for (i,j,t) in X if (j,t) in E and not E[j,t]) ==0)

# EnsureDropoffAtEachSchool = {j: 
#     m.addConstr(gp.quicksum(X[i, j, t] for i, _, t in X if (i,j,t) in X) >= 1) 
#     for j in N
# }

# for j in [50, 52, 54, 54, 55, 56, 57]:
#     print(j, DELTA_MINUS[j])

for j in N:
    if j in [50, 52, 53, 54, 54, 55, 56, 57]:
        print("\nWHATS DIFFERENT,", j)
    else:
        print(f"\n{j}")
    for t in T:
        print(t, E[j, t])
    print()


# for j in N:
#     for t in T:
#         for i in DELTA_MINUS[j]:
#             print(i, j, t)
#             X[i, j, t]

# for j in N_FINAL:


TripDoneWithValidBus = {j: 
    m.addConstr(gp.quicksum(E[j, t] * X[i, j, t] for t in T for i in DELTA_MINUS[j] if (i,j,t) in X) == 1) 
    for j in N_FINAL
}


for j in N_FINAL:
    for t in T:
        gp.quicksum(X[i, j, t] for i in DELTA_MINUS[j] if (i, j, t) in X)
        gp.quicksum(X[j, i, t] for i in DELTA_PLUS[j] if (j, i, t) in X)

FlowBalance = {(j, t): 
    m.addConstr(gp.quicksum(X[i, j, t] for i in DELTA_MINUS[j] if (i, j, t) in X) == gp.quicksum(X[j, i, t] 
    for i in DELTA_PLUS[j] if (j, i, t) in X)) for j in N_FINAL for t in T
}


TimeWindowBound = {(i): m.addConstr(
    gp.quicksum(
        Z[i, j, EARLY] * WINDOW[i][SCHOOL_START_TIME] + 
        Z[i, j, LATE] * (WINDOW[j][SCHOOL_END_TIME] - P[i] - D[i, j]) for j in N_FINAL # this was the problem
    ) >= gp.quicksum(
        Z[j, i, EARLY] * (WINDOW[j][SCHOOL_START_TIME] + P[j] + D[j, i]) + 
        Z[j, i, LATE] * (WINDOW[i][SCHOOL_END_TIME] ) for j in N))
    for i in N 
}

FractionalBoundSum = {(i, j): 
    m.addConstr(Z[i, j,EARLY] + Z[i, j, LATE] == gp.quicksum(X[i, j, t] for t in T if (i, j, t) in X))
    for i, j, _ in X
}

StartAtDepot = {t: 
    m.addConstr(gp.quicksum(X[0, j, t] for j in DELTA_PLUS[0] if (0, j, t) in X) <= NUM[t]) # change this to num_t and everythign works :)
    for t in T
}

EndAtDepot = {t: 
    m.addConstr(gp.quicksum(X[i, len(N) + 1, t] for i in DELTA_MINUS[len(N) + 1] if (i, len(N)+1, t) in X) == 
                gp.quicksum(X[0, j, t] for j in DELTA_PLUS[0] if (0, j, t) in X)) # 
    for t in T
}

m.optimize()

endTime = time.time()
print(f"Model solved in {(endTime - startTime):.2f}s")

print(f"Depots: {0}, {len(N) + 1}")
# Print out results.
if m.Status != gp.GRB.INFEASIBLE:
    num_busses = sum(round(X[i,j,k].x) for (i,j,k) in X if i==0)
    distancee = sum(P[i] + D[i, j] for (i,j,k) in X if round(X[i,j,k].x)==1)
    print("Number of busses: ", num_busses)
    print("Distance: ", distancee)
    pass
else:
    m.computeIIS()
    m.write("iismodel.ilp")
    
    print("-----------------------------------")
    print("TripDoneWithValidBus: ")
    for j in TripDoneWithValidBus:
        if TripDoneWithValidBus[j].IISConstr:
            print(f"TripDoneWithValidBus[{j}] is{' NOT' if not TripDoneWithValidBus[j].IISConstr else ''} in the IIS")
            pass
    print("-----------------------------------")

    # print("EnsureDropoffAtEachSchool: ")
    # for j in EnsureDropoffAtEachSchool:
    #     if EnsureDropoffAtEachSchool[j].IISConstr:
    #         print(f"EnsureDropoffAtEachSchool[{j}] is{' NOT' if not EnsureDropoffAtEachSchool[j].IISConstr else ''} in the IIS")
    #         pass
    print("-----------------------------------")
    print("Flow Balance: ")
    for j, k in FlowBalance:
        if FlowBalance[j, k].IISConstr:
            print(f"FlowBalance[{j, k}] is{' NOT' if not FlowBalance[j, k].IISConstr else ''} in the IIS")
            pass
    print('----------------------------------')
    print("TimeWindowBound: ")
    for i in TimeWindowBound:
        if TimeWindowBound[i].IISConstr:
            print(f"TimeWindowBound[{i}] is{' NOT' if not TimeWindowBound[i].IISConstr else ''} in the IIS")
            pass
    print('----------------------------------')
    print("FractionalBoundSum: ")
    for i, j in FractionalBoundSum:
        if FractionalBoundSum[i, j].IISConstr:
            print(f"FractionalBoundSum[{i, j}] is in the IIS")
            pass
        
    print('----------------------------------')

    print("StartAtDepot: ")
    for t in StartAtDepot:
        if StartAtDepot[t].IISConstr:
            print(f"StartAtDepot[{t}] is in the IIS")
            pass
    print('----------------------------------')
    print("EndAtDepot: ")

    for t in EndAtDepot:
        if EndAtDepot[t].IISConstr:
            print(f"EndAtDepot[{t}] is in the IIS")
            pass

    print('----------------------------------')
    