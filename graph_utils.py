import networkx as nx  # type: ignore
from type_aliases import (
    Graph,
    GraphElements,
    GraphElement
)


class Id_generator:
    def __init__(self) -> None:
        self._id = 1

    def reset(self) -> None:
        self._id = 1

    def increment_id(self) -> None:
        self._id += 1

    def generate_id(self) -> str:
        self.increment_id()
        return str(self._id - 1)


id_generator = Id_generator()
ADD_ATTRS = "additional_attributes"


def is_node(element: GraphElement) -> bool:
    return "source" not in element["data"] and "target" not in element["data"]


def is_removable_edge(edge: GraphElement, removable_edges: GraphElements) -> bool:
    for removable_edge in removable_edges:
        if removable_edge == edge:
            return True
    return False


def convert_networkx_to_cytoscape(graph: Graph) -> tuple[GraphElements, bool]:
    x_idx = 0
    y_idx = 1
    scaling_factor = 500
    cyto_nodes = []
    positions = nx.spring_layout(graph)
    if isinstance(graph, nx.DiGraph):
        directed = True
    else:
        directed = False
    id_generator.reset()
    for node in graph.nodes():
        # Get the node attributes from the NetworkX graph
        node_attrs = graph.nodes[node]
        if node_attrs.get("position", True):
            position_x = positions[node][x_idx] * scaling_factor
            position_y = positions[node][y_idx] * scaling_factor
        else:
            position_x = node_attrs["position"]["x"]
            position_y = node_attrs["position"]["y"]
            node_attrs.pop("position")
        if node_attrs.get("label", True):
            label = str(node)
        else:
            label = node_attrs["label"]
            node_attrs.pop("label")
        id_generator.increment_id()

        # Create a dictionary representing the Cytoscape node with the modified attributes
        cyto_node = {
            "data": {"id": str(node), "label": label, ADD_ATTRS: node_attrs},
            "position": {
                "x": position_x,
                "y": position_y,
            },
        }

        # Add the Cytoscape node to the list of nodes
        cyto_nodes.append(cyto_node)
    cyto_edges = []
    for edge in graph.edges():
        # Get the edge attributes from the NetworkX graph
        edge_attrs = graph.edges[edge]

        # Create a dictionary representing the Cytoscape edge with the modified attributes
        cyto_edge = {
            "data": {
                "source": str(edge[0]),
                "target": str(edge[1]),
                ADD_ATTRS: edge_attrs,
            }
        }

        # Add the Cytoscape edge to the list of edges
        cyto_edges.append(cyto_edge)
    return cyto_nodes + cyto_edges, directed


def edge_target_arrow_shape(directed: bool) -> str:
    if directed:
        return "triangle"
    return "none"


# LEGACY TEST FUNCTION
def convert_cytoscape_to_networkx(elements: GraphElements) -> Graph:
    # Create an empty NetworkX graph
    nx_graph = nx.Graph()

    # Add nodes to the graph
    for element in elements:
        if is_node(element):
            # This element is a node
            node_id, node_attrs = create_node_attributes(element)
            nx_graph.add_node(node_id, **node_attrs)
        else:
            # This element is an edge
            source_id = element["data"]["source"]
            target_id = element["data"]["target"]
            edge_attrs = {
                key: value for key, value in element["data"][ADD_ATTRS].items()
            }
            nx_graph.add_edge(source_id, target_id, **edge_attrs)

    return nx_graph


def convert_cytoscape_to_yaml_dict(elements: GraphElements, directed: bool) -> dict:
    nodes = {}
    edges = []
    x_offset = 0.0
    y_offset = 0.0
    for element in elements:
        if not is_node(element):
            continue
        x_pos = element["position"]["x"]
        y_pos = element["position"]["y"]
        if x_pos < x_offset:
            x_offset = x_pos
        if y_pos < y_offset:
            y_offset = y_pos

    x_offset = abs(x_offset)
    y_offset = abs(y_offset)

    for element in elements:
        if is_node(element):
            node_id, node_attrs = create_node_attributes(element, x_offset, y_offset)
            nodes[str(node_id)] = node_attrs
        else:
            edges.append(convert_edge_to_yaml_dict(element))

    yaml_dict = {
        "graph_params": {
            "loader": "hardcoded",
            "loader_params": {
                "settings": {"directed": directed},
                "targets": {},
                "nodes": nodes,
                "edges": edges,
            },
        }
    }
    return yaml_dict


def create_node_attributes(
    node: GraphElement, x_offset: float = 0.0, y_offset: float = 0.0
) -> tuple[str, dict]:
    node_id = node["data"]["id"]
    node_attrs = {key: value for key, value in node["data"][ADD_ATTRS].items()}
    node_attrs["position"] = dict()
    node_attrs["position"]["x"] = node["position"]["x"] + x_offset
    node_attrs["position"]["y"] = node["position"]["y"] + y_offset
    node_attrs["label"] = node["data"]["label"]
    return node_id, node_attrs


def convert_edge_to_yaml_dict(element: GraphElement) -> dict:
    result = dict()
    source_id = element["data"]["source"]
    target_id = element["data"]["target"]
    edge_attrs = {
        key: value
        for key, value in element["data"][ADD_ATTRS].items()
        if key != "nodes"
    }
    result["nodes"] = [source_id, target_id]
    result.update(edge_attrs)
    return result
