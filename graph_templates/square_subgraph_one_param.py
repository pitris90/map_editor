from square_subgraph import square_subgraph
import networkx # type: ignore

from typing import Optional


def square_subgraph_one_param(
    num_nodes: int, node_seed: int = 13, node_att: Optional[dict] = None
) -> networkx.DiGraph:
    """Square Subgraph One Param
    The graph nodes are randomly chosen points of grid of size ‹side_length› ⨉ ‹side_length›.
    ‹num_nodes› nodes are chosen. The graph edges are computed in the taxicab distance metric by
    default. Euclidean metric is set by ‹taxicab=False›.

    Args:
        Number of nodes - num_nodes: number of the chosen nodes
        Node RNG seed - node_seed: the seed for the random generator - for nodes
        Node Attributes - node_att: optional attributes updating the default values
    
    Returns:
        Graph: The generated networkx graph
    """
    num_targets = num_nodes // 2
    return square_subgraph(num_nodes, num_nodes, num_targets, node_att, node_seed)
