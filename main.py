import gurobipy as gp
from util import *

m = gp.Model("Heterogenous Bus Problem")

# TODO: Get these variables from parsing
K = dict()              # Busses (id -> capacity)
INIT_DEPOT = []         # Inital Depot
N = dict()              # Virtual stops (id -> pos)
N0 = N | INIT_DEPOT     # Virtual stops U Original depot
POS = dict()            # Vange(len(N))

DISTANCE = [[distance(N[i], N[j]) for j in N] for i in N]
M0 = 1 << 20 - 1
M = M0 << 12

X = {(i, j, k): 
    m.addVar(vtype=gp.GRB.BINARY)
    for i in N0 for j in N0 for k in K
}

W = {(i, k):
    m.addVar()
    for i in N for k in K
}

m.setObjective(gp.quicksum(DISTANCE[i][j] * X[i, j, k] for i in N for j in N for k in K) + M0 * gp.quicksum(X[0, j, k] for j in N for k in K))