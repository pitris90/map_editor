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

airport_template = html
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


app.layout = html.Div(
    [
        cyto.Cytoscape(
            id="graph-cytoscape",
            elements=[],
            style={"width": "100%", "height": "600px"},
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
    if networkx_data.get("loader") == "hardcoded":
        # different handling
        return networkx_data
    loader_function = function_dict[networkx_data["loader"]]
    print(inspect.signature(loader_function).parameters)
    print(networkx_data["loader_params"])
    graph = call_graph_function_with_params(loader_function, networkx_data["loader_params"])
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
    Input("save-graph-image", "n_clicks"),
    prevent_initial_call=True,
)
def save(_):
    return dcc.send_file("./hello.txt")


@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-graph", "contents"),
    State("upload-graph", "filename"),
)
def update_output(contents, filename):
    if contents is not None:
        # read the uploaded file and convert it to a NetworkX graph
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        network_data = yaml.safe_load(decoded)

        graph = handle_yaml_graph(network_data)
        # convert the NetworkX data to a Cytoscape-compatible JSON format
        # cy_data = json_graph.cytoscape_data(nx.DiGraph(network_data))

        # return the Cytoscape-compatible JSON data
        return network_data


if __name__ == "__main__":
    app.run_server(debug=True)
