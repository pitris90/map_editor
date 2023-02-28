from square_subgraph import square_subgraph

def square_subgraph_one_param(num_nodes, node_seed=13, node_att=None):
    num_targets = num_nodes // 2
    return square_subgraph(num_nodes, num_nodes,  num_targets, node_att, node_seed)
