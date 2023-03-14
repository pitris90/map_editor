import networkx as nx
from networkx.readwrite import json_graph
import dash_bootstrap_components as dbc
from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
from dash_extensions.enrich import DashProxy, MultiplexerTransform
import base64
import yaml
import json
import inspect
import os
import sys
import importlib
from typing import List, Dict

original_path = sys.path

# get the absolute path of the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))
folder_name = "graph_templates"
# join the current directory with the folder name
directory = os.path.join(current_dir, folder_name)
sys.path.append(directory)
function_dict = {}

for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(".py"):
        module_name = filename[:-3]  # remove the .py extension
        module = importlib.import_module(module_name)
        function = getattr(module, module_name)
        function_dict[module_name] = function

# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    transforms=[MultiplexerTransform()],
)

additional_attrs = "additional_attributes"

graph_templates = html.Div(
    [
        dcc.Dropdown(
            options=[
                {"label": "Airport with One Parameter", "value": "airport_one_param"}
            ],
            id="graph_layout_dropdown",
        ),
        html.Button("Generate Graph from Template", id="graph-generate-button"),
    ],
    id="modal_html_body",
)

test_elements2 = [{"data": {"id": "center", "label": "center", "add_data": False}}]

test_elements = [
    {
        "data": {
            "target": False,
            "memory": 4,
            "id": "center",
            "value": "center",
            "label": "center",
        }
    },
    {
        "data": {
            "target": False,
            "memory": 4,
            "id": "H_0_0",
            "value": "H_0_0",
            "label": "H_0_0",
        }
    },
    {
        "data": {
            "target": True,
            "value": "G_0_0_0",
            "attack_len": 1,
            "blindness": 0,
            "memory": 1,
            "id": "G_0_0_0",
            "label": "G_0_0_0",
        }
    },
    {
        "data": {
            "target": True,
            "value": "G_0_0_1",
            "attack_len": 1,
            "blindness": 0,
            "memory": 1,
            "id": "G_0_0_1",
            "label": "G_0_0_1",
        }
    },
    {
        "data": {
            "target": False,
            "memory": 4,
            "id": "H_1_0",
            "value": "H_1_0",
            "label": "H_1_0",
        }
    },
    {
        "data": {
            "target": True,
            "value": "G_1_0_0",
            "attack_len": 1,
            "blindness": 0,
            "memory": 1,
            "id": "G_1_0_0",
            "label": "G_1_0_0",
        }
    },
    {
        "data": {
            "target": True,
            "value": "G_1_0_1",
            "attack_len": 1,
            "blindness": 0,
            "memory": 1,
            "id": "G_1_0_1",
            "label": "G_1_0_1",
        }
    },
    {
        "data": {
            "target": False,
            "memory": 4,
            "id": "H_2_0",
            "value": "H_2_0",
            "label": "H_2_0",
        }
    },
    {
        "data": {
            "target": True,
            "value": "G_2_0_0",
            "attack_len": 1,
            "blindness": 0,
            "memory": 1,
            "id": "G_2_0_0",
            "label": "G_2_0_0",
        }
    },
    {
        "data": {
            "target": True,
            "value": "G_2_0_1",
            "attack_len": 1,
            "blindness": 0,
            "memory": 1,
            "id": "G_2_0_1",
            "label": "G_2_0_1",
        }
    },
    {"data": {"len": 1, "source": "center", "target": "H_0_0"}},
    {"data": {"len": 1, "source": "center", "target": "H_1_0"}},
    {"data": {"len": 1, "source": "center", "target": "H_2_0"}},
    {"data": {"len": 1, "source": "H_0_0", "target": "G_0_0_0"}},
    {"data": {"len": 1, "source": "H_0_0", "target": "G_0_0_1"}},
    {"data": {"len": 1, "source": "H_1_0", "target": "G_1_0_0"}},
    {"data": {"len": 1, "source": "H_1_0", "target": "G_1_0_1"}},
    {"data": {"len": 1, "source": "H_2_0", "target": "G_2_0_0"}},
    {"data": {"len": 1, "source": "H_2_0", "target": "G_2_0_1"}},
]

app.layout = html.Div(
    [
        cyto.Cytoscape(
            id="graph-cytoscape",
            elements=test_elements2,
            style={"width": "100%", "height": "600px"},
            layout={"name": "circle"},
            autoRefreshLayout=True,
        ),
        html.Button("New Graph", id="new-graph-button"),
        dcc.Upload(id="upload-graph", children=html.Button("Upload Graph")),
        dcc.Download(id="save-graph"),
        html.Button("Download Graph", id="save-graph-image"),
        dbc.Button("Open modal", id="open"),
        dbc.Modal(
            [
                dbc.ModalHeader("Graph Templates"),
                dbc.ModalBody(children=graph_templates),
                dbc.ModalFooter(
                    dbc.Button("CLOSE BUTTON", id="close", className="ml-auto")
                ),
            ],
            id="modal",
        ),
        html.Div(id="output-data-upload"),
    ]
)


def handle_yaml_graph(networkx_data: Dict):
    networkx_data = networkx_data.get("graph_params", None)
    if networkx_data is None:
        print("Bad yaml file")
        return
    if networkx_data.get("loader") == "hardcodedxx":
        # different handling
        return networkx_data
    loader_function = function_dict[networkx_data["loader"]]
    print(inspect.signature(loader_function).parameters)
    print(networkx_data["loader_params"])
    graph = call_graph_function_with_params(
        loader_function, networkx_data["loader_params"]
    )
    return graph


def call_graph_function_with_params(func_reference, param_dict):
    params = inspect.signature(func_reference).parameters  # get function parameters
    kwargs = {}
    for name, param in params.items():
        if name in param_dict:
            # use parameter value from dictionary
            kwargs[name] = param_dict[name]
        elif param.default is not inspect.Parameter.empty:
            # use default value for optional parameter
            kwargs[name] = param.default
        else:
            # parameter is required but not present in dictionary
            raise ValueError(f"Missing required parameter '{name}'")
    return func_reference(**kwargs)  # call the function with the extracted arguments


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("save-graph", "data"),
    [Input("save-graph-image", "n_clicks"), State("graph-cytoscape", "elements")],
    prevent_initial_call=True,
)
def save(_, elements):
    yaml_dict = convert_cytoscape_to_yaml_dict(elements)
    return dcc.send_string(yaml.dump(yaml_dict), "graph.yml")


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("upload-graph", "contents"),
        State("upload-graph", "filename"),
        State("graph-cytoscape", "elements"),
    ],
    prevent_initial_call=False,
)
def update_output(contents, filename, elements):
    if contents is None:
        return []
        # read the uploaded file and convert it to a NetworkX graph
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    network_data = yaml.safe_load(decoded)
    graph = handle_yaml_graph(network_data)
    cytoscape_graph = nx.cytoscape_data(graph)
    # convert the NetworkX data to a Cytoscape-compatible JSON format
    # cy_data = json_graph.cytoscape_data(nx.DiGraph(network_data))
    data = []
    # return the Cytoscape-compatible JSON data

    elements = (
        cytoscape_graph["elements"]["nodes"] + cytoscape_graph["elements"]["edges"]
    )
    xdelements = (
        cytoscape_graph["elements"]["nodes"] + cytoscape_graph["elements"]["edges"]
    )
    test_data = convert_networkx_to_cytoscape(graph)
    xdgraph = convert_cytoscape_to_networkx(test_data)
    elements = test_data
    return elements


def convert_networkx_to_cytoscape(graph: nx.Graph):
    cyto_nodes = []
    for node in graph.nodes():
        # Get the node attributes from the NetworkX graph
        node_attrs = graph.nodes[node]

        # Create a dictionary representing the Cytoscape node with the modified attributes
        cyto_node = {
            "data": {"id": node, "label": str(node), additional_attrs: node_attrs}
        }

        # Add the Cytoscape node to the list of nodes
        cyto_nodes.append(cyto_node)
    cyto_edges = []
    for edge in graph.edges():
        # Get the edge attributes from the NetworkX graph
        edge_attrs = graph.edges[edge]

        # Create a dictionary representing the Cytoscape edge with the modified attributes
        cyto_edge = {
            "data": {"source": edge[0], "target": edge[1], additional_attrs: edge_attrs}
        }

        # Add the Cytoscape edge to the list of edges
        cyto_edges.append(cyto_edge)
    return cyto_nodes + cyto_edges


def convert_cytoscape_to_networkx(elements):
    # Create an empty NetworkX graph
    nx_graph = nx.Graph()

    # Add nodes to the graph
    for element in elements:
        if is_node(element):
            # This element is a node
            node_id = element["data"]["id"]
            node_attrs = {
                key: value for key, value in element["data"][additional_attrs].items()
            }
            nx_graph.add_node(node_id, **node_attrs)
        else:
            # This element is an edge
            source_id = element["data"]["source"]
            target_id = element["data"]["target"]
            edge_attrs = {
                key: value for key, value in element["data"][additional_attrs].items()
            }
            nx_graph.add_edge(source_id, target_id, **edge_attrs)

    return nx_graph


def convert_cytoscape_to_yaml_dict(elements):
    # temporary - now only converting to non directed graph settings
    nodes = {}
    edges = []
    for element in elements:
        if is_node(element):
            node_id = element["data"]["id"]
            node_attrs = {
                key: value for key, value in element["data"][additional_attrs].items()
            }
            nodes[str(node_id)] = node_attrs
        else:
            edges.append(convert_edge_to_yaml_dict(element))

    yaml_dict = {
        "graph_params": {
            "loader": "hardcoded",
            "loader_params": {
                "settings": {"directed": False},
                "targets": {},
                "nodes": nodes,
                "edges": edges,
            },
        }
    }
    return yaml_dict


def is_node(element):
    return "source" not in element["data"] and "target" not in element["data"]


def convert_edge_to_yaml_dict(element):
    result = {}
    source_id = element["data"]["source"]
    target_id = element["data"]["target"]
    edge_attrs = {
        key: value
        for key, value in element["data"][additional_attrs].items()
        if key != "nodes"
    }
    result["nodes"] = [source_id, target_id]
    result.update(edge_attrs)
    return result


@app.callback(
    Output("output-data-upload", "children"),
    [
        Input("new-graph-button", "n_clicks"),
        State("graph-cytoscape", "elements"),
        State("graph-cytoscape", "tapNodeData"),
    ],
)
def test_graph(n, elements, node_data):
    if n:
        print(elements)
        print("\n")
        print(node_data)
        return "Klik"
    return "Neklik"


if __name__ == "__main__":
    app.run_server(debug=True)
