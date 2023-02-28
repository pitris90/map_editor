import networkx

def diamond(values, node_att=None, target_att=None, edge_att=None):
    node_attribute = dict(target=False, memory=len(values))
    node_attribute.update(node_att or {})
    target_attribute = dict(target=True, value=1, memory=1, attack_len=1, blindness=0.0)
    target_attribute.update(target_att or {})
    edge_attribute = dict(len=1)
    edge_attribute.update(edge_att or {})

    nodes = [('start', node_attribute), ('stop', node_attribute)]
    edges = [('stop', 'start', edge_attribute)]
    for idx, val in enumerate(values):
        n_att = target_attribute.copy()
        n_att['value'] = val
        name = f"n_{idx}_v_{val}"
        nodes.append((name, n_att))
        edges.append(('start', name, edge_attribute))
        edges.append((name, 'stop', edge_attribute))
    graph = networkx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph