import networkx

def diamond_ring(values, node_att=None, target_att=None, edge_att=None):
    node_attribute = dict(target=False, memory=max(map(len, values)))
    node_attribute.update(node_att or {})
    target_attribute = dict(target=True, value=1, memory=1, attack_len=1, blindness=0.0)
    target_attribute.update(target_att or {})
    edge_attribute = dict(len=1)
    edge_attribute.update(edge_att or {})

    nodes = [('start', node_attribute)]
    edges = []
    start_node = 'start'
    for d_idx, one_diamond in enumerate(values):
        if d_idx == len(values)-1:
            end_node = nodes[0][0]
        else:
            end_node = f"d_{d_idx}"
            nodes.append((end_node, node_attribute))
        for v_idx, val in enumerate(one_diamond):
            n_att = target_attribute.copy()
            n_att['value'] = val
            name = f"d_{d_idx}_n_{v_idx}_v_{val}"
            nodes.append((name, n_att))
            edges.append((start_node, name, edge_attribute))
            edges.append((name, end_node, edge_attribute))
        start_node = end_node
    graph = networkx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph
