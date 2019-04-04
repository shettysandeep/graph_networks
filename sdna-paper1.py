#! python3.6
#coding: utf-8

#-----
# Sandeep
# 11/15/2017
# Replication exercise of Yu-Xiao-2017
# Setting up a random network and a growing network using PA as described
# in the paper (also in Huang-Liu-2007)
#-----

# ## SDNA PAPER EVALUATION - 11/13/2017


import numpy as np
import pandas as pd
import networkx as nx
import random
import matplotlib.pyplot as plt
from itertools import chain

# ### Generating a random network with communities [Liu & Hu, 2005]


def graph_gen_random(n_nodes =30, n_groups =3, prob_in = 0.10, prob_ac = 0.03):
    
    '''
    Parameters:
    ----------
    n_nodes: Number of nodes
    n_groups: Number of communities
    prob_in: Probability of connections within communities
    prob_out: Probability of connections across communities.
    
    Note: prob_out << prob_in
        
    Output: 
    -------
    Networkx Graph Object
    
    Notes:
    ------
    The approach is as follows: 
    - Generate nodes and assign them to groups
    - Within group connect the nodes with a high probability
    - Put them into a graph (leverage Networkx graph)
    - Iterate over all the nodes of the graph to assign connections to nodes
       across the groups at a lower selected probability.
    
    '''

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
                if nodes1 > nodes and random.uniform(0,1)<prob_in:
                    list_nodes.append((nodes, nodes1))

    # Add the nodes to a graph
    G = nx.Graph()
    G.add_edges_from(list_nodes)

    # Take all the nodes and connect them across groups
    for nodes in G.nodes():
        for nodes1 in G.nodes():
            if nodes1 > nodes and (random.uniform(0,1)<prob_ac) :
                G.add_edge(nodes,nodes1)

    return G

#testing = graph_gen_random() 
#print(testing.nodes(data=True))

#--------------------- END of function graph_gen_random --------------


#--------------------------------------------------------------------
# ### Generating a scale free network with communities [Huang & Li, 2007]

def graph_gen_pa(n_nodes = 100, n_groups=5, max_nodes = 200): 

    '''
    Parameters:
    ----------
    n_nodes: Number of nodes
    n_groups: Number of communities
    max_nodes: maximum nodes to grow (reach)   
    
        
    Output: 
    -------
    Networkx Graph Object
    
    Notes:
    ------
    The approach is as follows: 
    - Initialize a collection of nodes with within and across community
    connections
    - Grow network each period by adding one node with 'm_edge_in' connections
      within community and 'm_edge_out' inter-community connections. For now
      these two values on edges is decided by the program
    - Draw these connections randomly from the intial set while expanding
      the network size as new connections are formed
    - Store them in DataFrame and NetowrkX Graph object 
    - Return Graph object (change code if you want DataFrame) or both
    
    '''


#### Step 1 Initialization of communities 
   
    lt = [(i,random.randint(1,n_groups)) for i in range(1, n_nodes+1)]

    # no zero as node

    # take each list within a list and create a tuple among them

    groups = set([gr for nr,gr in lt])

    newlist = []
    newlist2 = []
    
    for gr in groups:
        newlist.append([(node,gr) for node,group in lt if group == gr])
        newlist2.append([node for node,group in lt if group == gr])


    # This list of tuples will hold all the graph nodes and properties


    list_nodes = []
    for items in newlist:
        for nodes,gr2 in items:
            for nodes1,gr3 in items:
                if nodes1 > nodes:
                    list_nodes.append((nodes, nodes1,gr2, gr3))


    # Adding inter-community links (M(M-1)/2)

    for index1, items1 in enumerate(newlist):
        node1,group1 = random.choice(items1) 
        for index2, items2 in enumerate(newlist):
            if index2 > index1:
                node2,group2 = random.choice(items2) 
                list_nodes.append((node1,node2,group1,group2))    

#### Step 2: grow the network & step  3: (PA -- inner community, -- intra community)

    # generate random number of link (FIXED) each time step
    n_edges_in = min([len(items) for items in newlist]) # from the same community, # number of edges  within community (FIXED)

    # one link across each community - Fix the # of 
    n_edges_out = random.choice(list(groups)) 

    # the final list of all nodes is in "list_nodes (list of tuples - source, target, community of source, community of target)"

    newnodes = []  # within community connections
    outnodes = [] # inter  community connections



    for i in range(n_nodes, max_nodes+1):
    # within community connections
    
    # choose random community to add new node
        rn = random.randint(1,3)
        lt_nd = list(np.random.choice(newlist2[rn],n_edges_in, replace=False))
    
    #newlist[rn].append((i,rn))  #updates the newlist
        for elements in lt_nd:
            newnodes.append((i,elements, rn)) # add this to the list
            list_nodes.append((i,nodes, rn, rn)) # adding to the container the domestic nodes (within community)
        
        
        newlist2[rn].extend(lt_nd)  # extending the sampling frame for the next round 
    
        # across community connections
        # collecting nodes that have outside connections
        # set up for outside communitity connections
        
        out_nodes = [(it,it1,it2,it4) for it,it1,it2,it4 in list_nodes if it2 != it4]
        out1 = [(items, items2) for items, items2,it3,it4 in out_nodes] 
        out2 = [items for items in chain(*out1)] # new sample to draw from - list of nodes
    
        out3 = [items for items in out2 if items not in newlist2[rn]] # all nodes outside the node's groups
        out_nd = list(np.random.choice(out3, n_edges_out, replace = False))
    
        #out2.append(out_nd) # expands the sample frame in the next round 
    
        for nodes in out_nd:
            for index, n1 in enumerate(newlist2):
                if nodes in newlist2[index]:
                    nd = index + 1
            outnodes.append((i,nodes, rn, nd))
            list_nodes.append((i,nodes, rn, nd)) # adding to the container international nodes

    #### Converting into Panda data frame (easier to view the structure)

    lt1 = pd.DataFrame(list_nodes, columns = ['node_start','node_end', 'groupofstartnode','groupofendnode'])

    # UNCOMMENT IF YOU NEED THIS INFORMATION 

    # Calculate within-community degree for each node - This will be required for the PA growth

    # Degree within community
    lt1['degreestart'] = lt1.groupby(by=['groupofstartnode','node_start'])['node_start'].transform(len)

    # Degree outside community (inter-community degree)
    lt1['degree_out']= lt1[lt1['groupofstartnode'] != lt1['groupofendnode']].groupby('node_start')['node_start'].transform(len)
    #lt1[lt1['groupofstartnode'] != lt1['groupofendnode']]

    #### Putting in a NetworkX graph object

    G = nx.from_pandas_dataframe(
        lt1, source='node_start',
        target = 'node_end',
        edge_attr=['groupofstartnode','groupofendnode','degreestart'])


    return G

#----------- End of function graph_gen_pa (preferential attachment graph)


#------------ main function -----------------------------

def main():

    graph_gen_pa()


    #graph_gen_random()



#---------- Initializing the execution

if __name__ == "__main__":
    main()
