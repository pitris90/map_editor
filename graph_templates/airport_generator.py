import networkx

import random


def airport_generator(halls_in_legs, default_gate_att, default_hall_att, gates=2, rnd_values=False, seed=None):
    if seed is not None:
        random.seed(seed)
    nodes = [('center', default_hall_att)]
    edges = []
    for leg_index in range(len(halls_in_legs)):
        previous = nodes[0][0]
        for hall_index in range(halls_in_legs[leg_index]):
            # hall
            hall_name = f"H_{leg_index}_{hall_index}"
            nodes.append((hall_name, default_hall_att))
            edges.append((previous, hall_name, {'len': 1}))
            previous = hall_name
            # gates
            for gate_index in range(gates):
                if rnd_values:
                    default_gate_att.update(value=random.randint(5, 15)/10)
                g_name = f"G_{leg_index}_{hall_index}_{gate_index}"
                nodes.append((g_name, default_gate_att))
                edges.append((hall_name, g_name, {'len': 1}))
    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph
