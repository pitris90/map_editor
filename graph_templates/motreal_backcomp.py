import networkx
from graph_helper.distance import distance

from itertools import product
import random
import os
import math

def motreal_backcomp(kml_file_name, node_att=None, distance_unit='meters', rounding=100, seed=13):
    from xml.dom import minidom
    my_doc = minidom.parse(os.path.join(os.getcwd(), kml_file_name))
    coordinates = my_doc.getElementsByTagName('coordinates')
    names = my_doc.getElementsByTagName('name')[1:]
    num_nodes = len(coordinates)
    chosen_nodes = []

    for elem in coordinates:
        (y, x, _) = elem.firstChild.data.strip().split(',')
        chosen_nodes.append((float(y), float(x)))

    edges_dist = [math.ceil(distance(from_vert, to_vert, True, distance_unit)/rounding)
                  for from_vert, to_vert in product(chosen_nodes, chosen_nodes)]

    max_edge = max(edges_dist)
    mean_edge = sum(edges_dist) / (num_nodes * (num_nodes - 1))
    attack_time = int(2 * max_edge + mean_edge)

    if seed:
        random.seed(seed)
    costs = [random.randint(180, 200) for _ in range(num_nodes)]
    blinds = [random.randint(0, 20) / 100 for _ in range(num_nodes)]

    nodes = []
    edges = []
    for i in range(num_nodes):
        from_name = f'{i}_{names[i].firstChild.data}'
        node_attributes = dict(value=costs[i], attack_len=attack_time, blindness=blinds[i], memory=4, target=True)
        node_attributes.update(node_att or {})
        nodes.append((from_name, node_attributes))
        for j in range(i + 1, num_nodes):
            edges.append((from_name, f'{j}_{names[j].firstChild.data}', dict(len=round(edges_dist[i * num_nodes + j]))))

    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    return graph
