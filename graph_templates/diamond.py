import networkx

from typing import Optional


def diamond(
    values: list,
    node_att: Optional[dict] = None,
    target_att: Optional[dict] = None,
    edge_att: Optional[dict] = None,
) -> networkx.DiGraph:
    """Diamond
    Args:
        Target Values - values: List of target values
        Node Attributes - node_att: Dictionary of default node attributes
        Target Attributes - target_att: Dictionary of default target attributes
        Edge Attributes - edge_att: Dictionary of default edge attributes

    Returns:
        Graph: The generated networkx graph
    """
    node_attribute = dict(target=False, memory=len(values))
    node_attribute.update(node_att or {})
    target_attribute = dict(target=True, value=1, memory=1, attack_len=1, blindness=0.0)
    target_attribute.update(target_att or {})
    edge_attribute = dict(len=1)
    edge_attribute.update(edge_att or {})

    nodes = [("start", node_attribute), ("stop", node_attribute)]
    edges = [("stop", "start", edge_attribute)]
    for idx, val in enumerate(values):
        n_att = target_attribute.copy()
        n_att["value"] = val
        name = f"n_{idx}_v_{val}"
        nodes.append((name, n_att))
        edges.append(("start", name, edge_attribute))
        edges.append((name, "stop", edge_attribute))
    graph = networkx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph
