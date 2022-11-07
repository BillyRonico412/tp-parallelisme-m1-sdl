import math

from matplotlib import pyplot as plt
import networkx as nx
from mpi4py import MPI


def plot_graph(graph, save=False, display=True):
    g1 = graph
    plt.tight_layout()
    nx.draw_networkx(g1, arrows=True)
    if save:
        plt.savefig("graph.png", format="PNG")
    if display:
        plt.show(block=True)


def split(x, size):
    n = math.ceil(len(x) / size)
    return [x[n * i:n * (i + 1)] for i in range(size - 1)] + [x[n * (size - 1):len(x)]]


# graph = nx.scale_free_graph(20).reverse()
# Generer les noeuds du graphe

# graph = nx.random_k_out_graph(20, 2, .8).reverse()

comm = MPI.COMM_WORLD

rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    graph = nx.gnr_graph(30, .01).reverse()
else:
    graph = None

graph = comm.bcast(graph, root=0)

new_elements = [0]  # We start at the root (node = 0) (A synchro)
old_elements = []  # We initialize the already seen nodes (A Synchro)

while len(new_elements) != 0:  # as long as we have new node

    if rank == 0:
        new_elements_split = split(new_elements, size)
    else:
        new_elements_split = None

    local_new_elements = comm.scatter(new_elements_split, root=0)

    tmp = []

    for node_src in local_new_elements:  # we take all these nodes
        for node in graph.neighbors(node_src):  # we take all their descendents
            if not node in old_elements and not node in new_elements and not node in tmp:
                # If the descendent is not already seen, we keep it
                tmp.append(node)

    old_elements += list(set(comm.allreduce(new_elements, op=MPI.SUM)))
    new_elements = list(set(comm.allreduce(tmp, op=MPI.SUM)))

if rank == 0:
    print(len(old_elements) == len(graph))
    plot_graph(graph, save=True, display=True)
