import networkx
from graph_helper.distance import distance

from itertools import combinations
import math
import random


def kml_graph(kml_file_name, node_att=None, taxicab=False, distance_unit='meters', rounding=1, seed=None):
    """Graph from a kml file
        Exported from google maps
    Attributes:
        kml_file_name  path to the kml file
        node_att       optional attributes updating the default values
        seed           the seed for the random generator
        taxicab        usage of taxicab or Euclidean metric
        distance_unit  if not None, used as a parameter for convergence from GPS coordinates
                       ('meters', 'miles')
        rounding       distances rounding
    """
    if seed is not None:
        random.seed(seed)

    from xml.dom import minidom
    kml_file = minidom.parse(kml_file_name)
    # get names (the fist one is the Document name)
    names = kml_file.getElementsByTagName('name')[1:]
    names = [f'{i}_{name.firstChild.data}' for i, name in enumerate(names)]
    # get coordinates
    coordinates = kml_file.getElementsByTagName('coordinates')
    chosen_nodes = []
    for elem in coordinates:
        (x, y, _) = elem.firstChild.data.strip().split(',')
        # x and y are switched correctly, see documentation
        chosen_nodes.append((float(y), float(x)))

    edges_dist = [math.ceil(distance(from_node, to_node, taxicab, distance_unit)/rounding)
                  for from_node, to_node in combinations(chosen_nodes, 2)]

    attack_time = int(2 * max(edges_dist) + sum(edges_dist) / len(edges_dist))

    nodes = []
    for name in names:
        node_attributes = dict(value=random.randint(90, 100),
                               attack_len=attack_time,
                               blindness=0.0, memory=4, target=True)
        node_attributes.update(node_att or {})
        nodes.append((name, node_attributes))

    edges = []
    for (from_name, to_name), dist in zip(combinations(names, 2), edges_dist):
        edge_attributes = dict(len=round(dist))
        edges.append((from_name, to_name, edge_attributes))

    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    return graph
