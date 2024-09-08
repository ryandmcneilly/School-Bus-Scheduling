import gurobipy as gp
from util import *

# Sets & Data
N, N_0, N_FINAL, N_ALL, K, E, P, D, DELTA_MINUS, DELTA_PLUS = read_file(1)

m = gp.Model("Heterogenous Bus Problem")

# Variables
X = {(i, j, k): m.addVar(gp.GRB.BINARY) for i in N_0 for j in N_FINAL for k in K}
W = {(i, k): m.addVar() for i in N for k in K}

# Constraints