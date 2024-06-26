import base64
import json
# import yaml  # type: ignore
import inspect
import re
import dash_bootstrap_components as dbc  # type: ignore
from typing import Optional
from type_aliases import (
    GraphElements,
    InputComponent
)
from dash_extensions.enrich import (  # type: ignore
    Output,
    Input,
    State,
    dcc,
    html
)
from app import app
from graph_utils import (
    convert_cytoscape_to_json,
    edge_target_arrow_shape,
    id_generator,
    # convert_cytoscape_to_yaml_dict,
    convert_networkx_to_cytoscape,
    json_to_networkx_graph
)
from graph_functions import (
    # handle_yaml_graph,
    FUNCTION_DICT,
    create_function_parameter_input_field,
    handle_input_dict,
    call_graph_function_with_params,
)


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
    json_dict = convert_cytoscape_to_json(elements, directed)
    return dcc.send_string(json.dumps(json_dict, indent=4), "graph.json")


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
    # network_data = yaml.safe_load(decoded)
    # graph = handle_yaml_graph(network_data)
    graph = json_to_networkx_graph(decoded)
    if graph is None:
        print("Graph after handling yaml was None")
        return [], directed, label, stylesheet
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


@app.callback(
    Output("input_fields", "children"),
    Input("graph_layout_dropdown", "value"),
    prevent_initial_call=True,
)
def create_input_fields(selected_option: str) -> list[InputComponent]:
    # using global constant
    input_fields: list = []
    if selected_option is None:
        return input_fields
    selected_function = FUNCTION_DICT[selected_option]
    doc = inspect.getdoc(selected_function)
    if doc is None:
        return input_fields
    pattern = r"\s*([\w\s]+\w)\s*-\s*(\w+)\s*:\s*(.+)"
    parameters = re.findall(pattern, doc, flags=re.MULTILINE)
    for parameter in parameters:
        name, py_name, desc = parameter[0], parameter[1], parameter[2]
        input_fields.append(
            html.Label(name, className="label", id="param_label_" + py_name)
        )
        input_fields.append(dbc.Tooltip(desc, target="param_label_" + py_name))
        type_annotation = (
            inspect.signature(selected_function).parameters[py_name].annotation
        )
        input_fields.append(
            create_function_parameter_input_field(
                py_name, type_annotation, selected_function
            )
        )
    return input_fields


def button_click(
    n_clicks: int,
    value: str,
    html_input_children: list[InputComponent],
    stylesheet: list[dict],
) -> tuple[GraphElements, bool, bool, str, list[dict]]:
    print(html_input_children)
    if n_clicks is None or html_input_children is None:
        return [], False
    param_dict = {}
    for child in html_input_children:
        if child["type"] == "Label" or child["type"] == "Tooltip":
            continue
        param_name, param_value = handle_input_dict(child)
        param_dict[param_name] = param_value
    graph = call_graph_function_with_params(FUNCTION_DICT[value], param_dict)
    cytoscape_elements, directed = convert_networkx_to_cytoscape(graph)
    label, stylesheet = graph_orientation_switcher(directed, stylesheet)
    return cytoscape_elements, False, directed, label, stylesheet


@app.callback(
    Output("modal_menu_graph_functions", "is_open"),
    [Input("open", "n_clicks")],
    [State("modal_menu_graph_functions", "is_open")],
)
def toggle_modal(n1: Optional[int], is_open: bool) -> bool:
    return n1 is not None
