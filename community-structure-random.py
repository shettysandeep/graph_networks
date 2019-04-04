#! python3.6
# SANDEEP - 11/13/17

import pandas as pd
import networkx as nx
import numpy as np
import random

'''
Writing code to generate Graphs with commnunites. WRITE A BETTER
DECSRIPTION OF THIS SCRIPT

Nodes - number of nodes
M - number of subgroups or communities
p - probability of link within communities
q - prob of link across community 

p >> q


The approach is as follows: 
    Generate nodes and assign them to groups
    Within group connect the nodes with a high probability
    Put them into a graph
    Iterate over all the nodes of the graph to assign connections to nodes
    across the groups at a lower selected probability.

'''

def graph_gen_random(n_nodes =30, n_groups =3, prob_in = 0.10, prob_ac = 0.03):

    lt = [(i,random.randint(1,n_groups)) for i in range(1, n_nodes+1) ] 

    groups = set([gr for nr,gr in lt])

# Create a list of list of tuples of nodes (nodes within a group) This now gives me
# the distribution of nodes in the various groups for future use.

    newlist = []

    for gr in groups:
        newlist.append([node for node,group in lt if group == gr])

 
# Create data structure (of nodes) that can be consumed by the NetworkX
# graph class 

#take each list within a list and create a tuple among them

    list_nodes = []
    for items in newlist:
        for nodes in items:
            for nodes1 in items:
                if nodes!=nodes1 and random.uniform(0,1)<prob_in:
                    list_nodes.append((nodes, nodes1))

# Add the nodes to a graph
    G = nx.Graph()
    G.add_edges_from(list_nodes)

# Take all the nodes and connect them across groups
    for nodes in G.nodes():
        for nodes1 in G.nodes():
            if nodes!=nodes1 and (random.uniform(0,1)<prob_ac) :
                G.add_edge(nodes,nodes1)

    return G

#testing = graph_gen_random() 
#print(testing.nodes(data=True))
