import numpy as np
from enum import IntEnum

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
   return np.linalg.norm(pos1 - pos2)


# Read csv
def read_file(test_number):
   test_filename = f"./datasets/hetero_test_file{test_number}.txt"
   vehicle_filename = f"./datasets/hetero_vehicle_file{test_number}.txt"

   test_file = np.loadtxt(test_filename, skiprows=1, dtype=np.uint16)
   vehicle_file = np.loadtxt(vehicle_filename, skiprows=1, dtype=np.uint16)

   # Construct N, E, delta+, delta-
   N = set(test_file[:, Test.ID])
   K = set(vehicle_file[:, Vehicle.VEH_ID])

   E = {(i, j): test_file[i - 1][Test.STUDENT_NUM] < vehicle_file[j - 1][Vehicle.CAPACITY] 
        for i in N for j in K
   }
   
   
   return N, K, E


print(read_file(1))