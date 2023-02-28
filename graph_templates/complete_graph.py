import networkx
from itertools import combinations

def complete_graph(num_nodes, node_att=None):
    node_attributes = dict(value=100, attack_len=num_nodes, blindness=0.0, memory=1, target=True)
    node_attributes.update(node_att or {})
    edge_attributes = dict(len=1)
    graph = networkx.Graph()
    nodes = list(range(num_nodes))
    edges = combinations(nodes, 2)
    graph.add_nodes_from(nodes, **node_attributes)
    graph.add_edges_from(edges, **edge_attributes)
    graph.name = f'{num_nodes}_clique'
    return graph
