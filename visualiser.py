from pyvis.network import Network

from reportImplementation import *

# Need some trip id, value (colour based on degree), title (id), x, y, label, colour (z)


# 1 = FF0000
net = Network()
net.add_nodes(range(1, len(N) + 1), value=[sum([X[i, j, k].x for j in N for k in K]) for i in N ], 
              title=range(1, len(N) + 1), 
              x=[SCHOOL_POSITIONS[i][0] for i in N], 
              y=[SCHOOL_POSITIONS[i][1] for i in N], 
              label=[f"School {i}" for i in N], #color=[f"rgb({sum([Z[i, j, LATE].x for j in N] for i in N) / 255}, 00, {sum([Z[i, j, EARLY].x for j in N] for i in N) / 255})"])
)

net.show('network.html')
