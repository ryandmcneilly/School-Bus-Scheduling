from pyvis.network import Network
from main import *  # Assuming this imports necessary data and variables

net = Network(directed=True)

net.add_node(f"Depot", color="#808080", title="Bus Depot", x=DEPOT_POSITION[0], y=DEPOT_POSITION[1])

for i in N:
    net.add_node(f"{i}", title=f"School {int(i)}", 
                 x=float(SCHOOL_POSITIONS[i][0]), y=float(SCHOOL_POSITIONS[i][1]),
                 label=f"School {i}")

for i in N:
    for j in N:
        for t in T:
            if X[i, j, t].x > 0:
                net.add_edge(str(i), str(j), title=f"Bus type {t}")

# net.toggle_physics(False)

# Display the network
net.show('network.html')
