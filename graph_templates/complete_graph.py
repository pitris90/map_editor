import networkx
from itertools import combinations
from typing import Optional

def complete_graph(num_nodes: int, node_att: Optional[dict]=None) -> networkx.Graph:
    """Complete Graph
    Args:
        Number of nodes - num_nodes: Amount of graph nodes
        Node attributes - node_att: Dictionary of node attributes

    Returns:
        Graph: The generated networkx graph
    """
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
