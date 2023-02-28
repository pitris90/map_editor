import networkx


def airport(hall_distances, gates, default_gate_att, default_hall_att):
    nodes = [('center', default_hall_att)]
    edges = []
    # building halls
    for leg_index, leg in enumerate(hall_distances):
        previous = nodes[0][0]
        for hall_index, hall_distance in enumerate(leg):
            new_node = f"H_{leg_index}_{hall_index}"
            nodes.append((new_node, default_hall_att))
            edges.append((previous, new_node, {'len': hall_distance}))
            previous = new_node
    # building gates
    for leg_index, leg in enumerate(gates):
        for hall_index, hall_gates in enumerate(leg):
            hall_name = f"H_{leg_index}_{hall_index}"
            for gate in hall_gates:
                g_name = gate.pop('name')
                g_dist = gate.pop('dist')
                g_att = default_gate_att.copy()
                g_att.update(gate)
                nodes.append((g_name, g_att))
                edges.append((hall_name, g_name, {'len': g_dist}))
    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph
