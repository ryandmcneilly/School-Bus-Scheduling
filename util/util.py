import numpy as np
from enum import IntEnum

BUS_SPEED = 60 # km/h

class Test(IntEnum):
   ID = 0
   START_X = 1
   START_Y = 2
   STUDENT_NUM = 3
   SERVICE_DURATION = 4
   SCHOOL_X = 5
   SCHOOL_Y = 6
   SCHOOL_TW_ST = 7
   SCHOOL_TW_END = 8

class Vehicle(IntEnum):
   VEH_ID = 0
   DEPOT_X = 1
   DEPOT_Y = 2
   CAPACITY = 3


# Euclidean distance between two virtual stops
def distance(pos1, pos2):
   return int(np.linalg.norm(np.array((pos1[0] - pos2[0], pos1[1] - pos2[1]))))

# Read csv
def read_file(test_number):
   test_filename = f"./datasets/sorted/sorted_hetero_test_file{test_number}.txt"
   vehicle_filename = f"./datasets/original/hetero_vehicle_file{test_number}.txt"

   test_file = np.loadtxt(test_filename, skiprows=1, dtype=np.int32)
   vehicle_file = np.loadtxt(vehicle_filename, skiprows=1, dtype=np.int32)

   # Construct N, E, delta+, delta-
   N = set(test_file[:, Test.ID])
   N_0 = N | {0}
   N_FINAL = N | {len(N) + 1}
   N_ALL = {0} | N | {len(N) + 1}

   K = set(vehicle_file[:, Vehicle.VEH_ID])

   # Stores if bus k has enough capacity for stop i
   E = {(i, k): test_file[i - 1][Test.STUDENT_NUM] < vehicle_file[k - 1][Vehicle.CAPACITY] 
        for i in N for k in K
   }

   # Time window constraints
   P = {row[Test.ID]: row[Test.SERVICE_DURATION] for row in test_file}
   WINDOW = {row[Test.ID]: (row[Test.SCHOOL_TW_ST], row[Test.SCHOOL_TW_END]) for row in test_file}

   SCHOOL_POSITIONS = {row[Test.ID]: (row[Test.SCHOOL_X], row[Test.SCHOOL_Y]) for row in test_file}
   SCHOOL_POSITIONS[0] = (0, 0) # Depot set to origin coordinate for ease.

   START_POSITIONS = {row[Test.ID]: (row[Test.START_X], row[Test.START_Y]) for row in test_file}
   START_POSITIONS[len(N) + 1] = (0, 0) # Depot set to origin coordinate for ease.

   # Time from School i to start of trip j
   D = {(i, j):
        0 if (i == 0 or j == len(N) + 1) else distance(SCHOOL_POSITIONS[i], START_POSITIONS[j]) 
        for i in N_0 for j in N_FINAL
   }

   # trip j can be preceded by trip i if 
   DELTA_MINUS = {j: {i for i in N if WINDOW[j][0] <= WINDOW[i][1] + P[j] + D[i, j]} | {0} for j in N }
   DELTA_PLUS = {j: {i for i in N if WINDOW[i][0] + D[i, j] + P[j] <= WINDOW[j][1]} | {len(N) + 1} for j in N }
   
   return N, N_0, N_FINAL, N_ALL, K, E, P, D, DELTA_MINUS, DELTA_PLUS, WINDOW