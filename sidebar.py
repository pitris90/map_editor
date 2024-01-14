import base64
import yaml  # type: ignore
from typing import Optional
from type_aliases import (
    GraphElements
)
from dash_extensions.enrich import (  # type: ignore
    Output,
    Input,
    State,
    dcc,
)
from app import app
from graph_utils import (
    edge_target_arrow_shape,
    id_generator,
    convert_cytoscape_to_yaml_dict,
    convert_networkx_to_cytoscape
)
from graph_functions import handle_yaml_graph


@app.callback(
    [
        Output("orientation-graph-switcher", "label"),
        Output("graph-cytoscape", "stylesheet"),
    ],
    [Input("orientation-graph-switcher", "on"), State("graph-cytoscape", "stylesheet")],
)
def graph_orientation_switcher(
    directed: bool, stylesheet: list[dict]
) -> tuple[str, list[dict]]:
    for selector in stylesheet:
        if selector["selector"] == "edge":
            selector["style"]["target-arrow-shape"] = edge_target_arrow_shape(directed)
            break
    if directed:
        return "Directed", stylesheet
    return "Undirected", stylesheet


@app.callback(
    Output("graph-cytoscape", "elements"),
    [Input("new-graph-button", "n_clicks"), State("graph-cytoscape", "elements")],
)
def new_graph(n: Optional[int], elements: GraphElements) -> GraphElements:
    if n is not None and n > 0:
        id_generator.reset()
        return []
    return elements


@app.callback(
    Output("save-graph", "data"),
    [
        Input("save-graph-image", "n_clicks"),
        State("graph-cytoscape", "elements"),
        State("orientation-graph-switcher", "on"),
    ],
    prevent_initial_call=True,
)
def save(_: Optional[int], elements: GraphElements, directed: bool) -> dict:
    yaml_dict = convert_cytoscape_to_yaml_dict(elements, directed)
    return dcc.send_string(yaml.dump(yaml_dict), "graph.yml")


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("orientation-graph-switcher", "on"),
        Output("orientation-graph-switcher", "label"),
        Output("graph-cytoscape", "stylesheet"),
    ],
    [
        Input("upload-graph", "contents"),
        State("upload-graph", "filename"),
        State("graph-cytoscape", "elements"),
        State("orientation-graph-switcher", "on"),
        State("orientation-graph-switcher", "label"),
        State("graph-cytoscape", "stylesheet"),
    ],
)
def update_output(
    contents: Optional[str],
    filename: Optional[str],
    elements: GraphElements,
    directed: bool,
    label: str,
    stylesheet: list[dict],
) -> tuple[GraphElements, bool, str, list[dict]]:
    if contents is None:
        return [], directed, label, stylesheet
        # read the uploaded file and convert it to a NetworkX graph
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    network_data = yaml.safe_load(decoded)
    graph = handle_yaml_graph(network_data)
    # cytoscape_graph = nx.cytoscape_data(graph)
    # convert the NetworkX data to a Cytoscape-compatible JSON format

    # return the Cytoscape-compatible JSON data

    # LEGACY TEST CODE
    # elements = (
    #     cytoscape_graph["elements"]["nodes"] + cytoscape_graph["elements"]["edges"]
    # )
    elements, directed = convert_networkx_to_cytoscape(graph)
    label, stylesheet = graph_orientation_switcher(directed, stylesheet)
    # test_graph = convert_cytoscape_to_networkx(elements)
    return elements, directed, label, stylesheet
