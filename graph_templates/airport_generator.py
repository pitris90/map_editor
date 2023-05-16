import networkx # type: ignore

import random
from typing import Optional


def airport_generator(
    halls_in_legs: list,
    default_gate_att: dict,
    default_hall_att: Optional[dict],
    gates: int = 2,
    rnd_values: bool = False,
    seed: Optional[int] = None,
) -> networkx.Graph:
    """Airport Generator
    Args:
        The Tree Structure - halls_in_legs: List of lists describing the tree structure of legs and their halls (the item values are ignored)
        Default Gate Attribute - default_gate_att: Dictionary of default gate attributes
        Default Hall Attribute - default_hall_att: Dictionary of default hall attributes
        Number of Gates - gates: The number of gates on each hall
        Random Values - rnd_values: If true, the values of gates are generated randomly.
        Seed - seed: The seed for pseudo-randomness, 'None' for an unseeded run.

    Returns:
        Graph: The generated networkx graph
    """
    if seed is not None:
        random.seed(seed)
    nodes = [("center", default_hall_att)]
    edges = []
    for leg_index in range(len(halls_in_legs)):
        previous = nodes[0][0]
        for hall_index in range(halls_in_legs[leg_index]):
            # hall
            hall_name = f"H_{leg_index}_{hall_index}"
            nodes.append((hall_name, default_hall_att))
            edges.append((previous, hall_name, {"len": 1}))
            previous = hall_name
            # gates
            for gate_index in range(gates):
                if rnd_values:
                    default_gate_att.update(value=random.randint(5, 15) / 10)
                g_name = f"G_{leg_index}_{hall_index}_{gate_index}"
                nodes.append((g_name, default_gate_att))
                edges.append((hall_name, g_name, {"len": 1}))
    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph
