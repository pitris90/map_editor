import networkx # type: ignore


def hardcoded(nodes, targets, edges, settings=None): # type: ignore
    nodes = nodes or {}
    targets = targets or {}
    edges = edges or {}
    settings = settings or {}
    node_att = settings.get('node_att', {}).copy()
    node_att.update(target=False)
    target_att = settings.get('target_att', {}).copy()
    target_att.update(target=True)
    edge_att = settings.get('edge_att', {}).copy()

    nodes = [(node, {**node_att, **(att or {})}) for node, att in nodes.items()]
    targets = [(target, {**target_att, **(att or {})}) for target, att in targets.items()]
    edges = [(*edge.get('nodes'), {**edge_att, **edge}) for edge in edges]

    directed = settings.get('directed', True)
    graph = networkx.DiGraph() if directed else networkx.Graph()
    graph.add_nodes_from(targets + nodes)
    graph.add_edges_from(edges)
    graph.name = 'hardcoded'

    return graph
