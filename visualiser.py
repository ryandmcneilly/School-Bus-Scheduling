from pyvis.network import Network
from main import *  # Assuming this imports necessary data and variables

# Initialize network object
net = Network(directed=True)

# Create nodes for the network based on the 'Z' and 'X' variables
for i in N:
    # Sum up the X[i,j,k] values to determine the size of the node (value)
    node_value = sum([X[i, j, k].x for j in N for k in K])

    # red = int(min(sum([Z[i, j, EARLY].x for j in N]), 255))
    # blue = int(min(sum([Z[i, j, LATE].x for j in N]), 255))
    # color = f"rgb({red}, 0, {blue})"

    # Add each node with respective attributes
    net.add_node(f"{i}", value=int(node_value), title=f"School {int(i)}", 
                 x=float(SCHOOL_POSITIONS[i][0]), y=float(SCHOOL_POSITIONS[i][1]),
                 label=f"School {i}", #color=color)
    )


for i in N:
    for j in N:
        for k in N:
            if X[i, j, k].x > 0:
                net.add_edge(str(i), str(j))
# Display the network
net.show('network.html')
