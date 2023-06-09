import networkx # type: ignore
from typing import Optional
from type_aliases import Graph

def circle_graph(num_nodes: int, node_att: Optional[dict]=None) -> Graph:
    """Circle Graph
    Args:
        Number of nodes - num_nodes: Amount of graph nodes
        Node attributes - node_att: Dictionary of node attributes

    Returns:
        Graph: The generated networkx graph
    """
    node_attributes = dict(value=100, attack_len=num_nodes, blindness=0.0, memory=1, target=True)
    node_attributes.update(node_att or {})
    graph = networkx.cycle_graph(num_nodes)
    for attr in node_attributes.keys():
        networkx.set_node_attributes(graph, values=node_attributes[attr], name=attr)
    networkx.set_edge_attributes(graph, values=1, name='len')
    graph.name = f'{num_nodes}_circle'
    return graph
