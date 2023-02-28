import networkx
from graph_helper.distance import distance

from itertools import product, combinations
import random


def square_subgraph(side_length, num_nodes, num_targets=None, node_att=None, node_seed=13, param_seed=13, taxicab=True,
                    blind=False):
    """Generates random graphs based on grids.
    The graph nodes are randomly chosen points of grid of size ‹side_length› ⨉ ‹side_length›.
    ‹num_nodes› nodes are chosen. The graph edges are computed in the taxicab distance metric by
    default. Euclidean metric is set by ‹taxicab=False›.

    Attributes:
        side_length    side length of the original grid
        num_nodes      number of the chosen nodes
        num_targets    number of targets ( <= num_nodes; if None, it equals to num_nodes)
        node_att       optional attributes updating the default values
        node_seed      the seed for the random generator - for nodes
        param_seed     the seed for the random generator - for parameters
        taxicab        usage of taxicab or Euclidean metric
        blind          True for random blindness in nodes
        verbose        True for printing the generated graph

    Backward compatibility:
       Sub_g_6_n_01.in is generated by square_subgraph(6, 10, node_seed=1)
    """
    # safety check
    if not (1 <= num_nodes <= side_length * side_length):
        raise AttributeError(f"Error: wrong value for parameter num_nodes, "
                             f"not (1 <= {num_nodes} <= {side_length * side_length}).")

    if num_targets is None:
        num_targets = num_nodes

    if num_nodes < num_targets:
        raise AttributeError(f"Error: wrong value for parameter num_targets, not ({num_targets} <= {num_nodes}).")

    # choose the nodes
    pool = [edge for edge in product(range(side_length), repeat=2)]
    random.seed(node_seed)
    random.shuffle(pool)
    chosen_nodes = pool[:num_nodes]
    chosen_targets = chosen_nodes[:num_targets]
    chosen_nodes.sort()

    # compute distances/edges
    edges_dist = [distance(*edge, taxicab=taxicab) for edge in combinations(chosen_nodes, 2)]

    # edge-length statistics
    max_edge = max(edges_dist)
    mean_edge = sum(edges_dist) / len(edges_dist)
    attack_time = int(max_edge + mean_edge + 3) if taxicab else int(2 * max_edge + mean_edge)

    random.seed(param_seed)

    nodes = []
    for node in chosen_nodes:
        node_attributes = dict(value=random.randint(180, 200),
                               attack_len=attack_time,
                               blindness=random.randint(0, 20) / 100 if blind else 0,
                               memory=4,
                               target=(node in chosen_targets))
        node_attributes.update(node_att or {})
        nodes.append((node, node_attributes))

    edges = []
    for edge, dist in zip(combinations(chosen_nodes, 2), edges_dist):
        edges.append((*edge, dict(len=dist)))

    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    graph = graph.to_directed()
    graph.name = f"square_subgraph_s{side_length}_n{num_nodes}_t{num_targets}"

    return graph
