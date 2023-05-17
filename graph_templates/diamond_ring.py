import networkx # type: ignore

from typing import Optional


def diamond_ring(
    values: list,
    node_att: Optional[dict] = None,
    target_att: Optional[dict] = None,
    edge_att: Optional[dict] = None,
) -> networkx.DiGraph:
    """Ring of Diamonds
    Args:
        List of Values - values: List of lists of values describing the structure of diamonds on the ring
        Node Attributes - node_att: Dictionary of default node attributes
        Target Attributes - target_att: Dictionary of default target attributes
        Edge Attributes - edge_att: Dictionary of default edge attributes

    Returns:
        Graph: The generated networkx graph
    """
    node_attribute = dict(target=False, memory=max(map(len, values)))
    node_attribute.update(node_att or {})
    target_attribute = dict(target=True, value=1, memory=1, attack_len=1, blindness=0.0)
    target_attribute.update(target_att or {})
    edge_attribute = dict(len=1)
    edge_attribute.update(edge_att or {})

    nodes = [("start", node_attribute)]
    edges = []
    start_node = "start"
    for d_idx, one_diamond in enumerate(values):
        if d_idx == len(values) - 1:
            end_node = nodes[0][0]
        else:
            end_node = f"d_{d_idx}"
            nodes.append((end_node, node_attribute))
        for v_idx, val in enumerate(one_diamond):
            n_att = target_attribute.copy()
            n_att["value"] = val
            name = f"d_{d_idx}_n_{v_idx}_v_{val}"
            nodes.append((name, n_att)) # type: ignore
            edges.append((start_node, name, edge_attribute))
            edges.append((name, end_node, edge_attribute))
        start_node = end_node
    graph = networkx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph
