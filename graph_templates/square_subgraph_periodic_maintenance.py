import networkx # type: ignore
from graph_helper.distance import distance # type: ignore

from itertools import product, combinations
from typing import Optional
import random


def square_subgraph_periodic_maintenance(
    side_length: int,
    depo_att: Optional[dict],
    num_target_groups: list,
    target_att_list: list,
    num_target_param: Optional[int] = None,
    node_seed: Optional[int] = None,
) -> networkx.DiGraph:
    """Square Subgraph for Periodic Maintenance
    Args:
        Side Length - side_length: Side length of the original grid
        Depo Attributes - depo_att: Dictionary of default depo attributes
        List of Numbers of Targets - num_target_groups: List of numbers of instances created of each type of target
        List of Target Attributes - target_att_list: List of dictionaries expressing attributes for types of targets
        Number of Targets - num_target_param: Optional number of instances created of each type of targets. If not None, it rewrites num_target_groups
        Node RNG seed - node_seed: the seed for the random generator - for nodes

    Returns:
        Graph: The generated networkx graph
    """
    if num_target_param is not None:
        num_target_groups = [num_target_param * x for x in num_target_groups]
    depo_att["target"] = True # type: ignore
    for att in target_att_list:
        att["target"] = True

    if len(num_target_groups) != len(target_att_list):
        raise AttributeError(
            f"Error: num_target_groups and target_att_list differ in length, "
            f"({len(num_target_groups)} != {len(target_att_list)})."
        )

    num_nodes = sum(num_target_groups)
    depo = (side_length // 2, side_length // 2)

    if not (1 <= num_nodes <= side_length * side_length - 1):
        raise AttributeError(
            f"Error: wrong value for parameter num_nodes, "
            f"not (1 <= {num_nodes} <= {side_length * side_length} - 1)."
        )

    # choose the nodes
    pool = [edge for edge in product(range(side_length), repeat=2)]
    pool.remove(depo)
    random.seed(node_seed)
    random.shuffle(pool)
    chosen_nodes = pool[:num_nodes]

    full_list_of_target_att = []
    for number, attributes in zip(num_target_groups, target_att_list):
        full_list_of_target_att.extend([attributes] * number)
    random.shuffle(full_list_of_target_att)

    nodes = [(depo, depo_att)]
    nodes += list(zip(chosen_nodes, full_list_of_target_att)) # type: ignore

    chosen_nodes.insert(0, depo)
    # compute distances/edges
    edges_dist = [
        distance(*edge, taxicab=True) for edge in combinations(chosen_nodes, 2)
    ]

    # self-loop for depo
    edges = [(depo, depo, dict(len=10))]
    for edge, dist in zip(combinations(chosen_nodes, 2), edges_dist):
        edges.append((*edge, dict(len=10 * dist))) # type: ignore

    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    graph = graph.to_directed()
    graph.name = f"grid_sl{side_length}_ntg{num_target_groups}"

    return graph
