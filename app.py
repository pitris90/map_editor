import networkx as nx  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

# from dash import dcc, html, Dash
# from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto  # type: ignore
import dash_daq as daq  # type: ignore
from dash_extensions.enrich import (  # type: ignore
    DashProxy,
    MultiplexerTransform,
    Output,
    Input,
    State,
    html,
    dcc,
)
import base64
import yaml  # type: ignore
import inspect
import os
import sys
import importlib
import re
import ast
import json
from typing import List, Dict, Callable, Any, Union, Optional, Tuple, Type
from type_aliases import (
    Graph,
    GraphFunction,
    GraphOrNone,
    GraphElements,
    InputComponent,
)
from functools import reduce


class DocError(ValueError):
    """Raised when the __doc__ attribute of an object is badly written."""

    pass


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


class Selected_items:
    def __init__(self) -> None:
        self._selected_common_attrs = []
        self._selected_elements = []
        self._selected_edges = []
        self._selected_nodes = []
        self._selected_elements_idxs = []

    def set_attrs(self, selected_common_attrs):
        self._selected_common_attrs = selected_common_attrs

    def get_attrs(self):
        return self._selected_common_attrs.copy()

    def set_elements(self, selected_elements):
        self._selected_elements = selected_elements

    def get_elements(self):
        return self._selected_elements.copy()

    def set_edges(self, selected_edges):
        self._selected_edges = selected_edges

    def get_edges(self):
        return self._selected_edges.copy()

    def set_nodes(self, selected_nodes):
        self._selected_nodes = selected_nodes

    def get_edges(self):
        return self._selected_nodes.copy()

    def generate_selected_elements_idxs(self, elements):
        selected_elements_idxs = []
        for i in range(0, len(elements)):
            self._append_idx_if_selected_element(elements, i, selected_elements_idxs)
        self._selected_elements_idxs = selected_elements_idxs

    def _append_idx_if_selected_element(
        self, elements, element_idx, selected_elements_idxs
    ):
        for selected_node in self._selected_nodes:
            if (
                is_node(elements[element_idx])
                and elements[element_idx]["data"]["id"] == selected_node["id"]
            ):
                selected_elements_idxs.append(element_idx)
        for selected_edge in self._selected_edges:
            if (
                not is_node(elements[element_idx])
                and elements[element_idx]["data"]["source"] == selected_edge["source"]
                and elements[element_idx]["data"]["target"] == selected_edge["target"]
            ):
                selected_elements_idxs.append(element_idx)

    def get_elements_idxs(self):
        return self._selected_elements_idxs


original_path = sys.path
# get the absolute path of the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))
folder_name = "graph_templates"
# join the current directory with the folder name
directory = os.path.join(current_dir, folder_name)
sys.path.append(directory)
function_dict = {}
selected_items = Selected_items()
id_generator = Id_generator()

for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(".py"):
        module_name = filename[:-3]  # remove the .py extension
        module = importlib.import_module(module_name)
        function = getattr(module, module_name)
        function_dict[module_name] = function


def dropdown_functions(function_dict: Dict[str, GraphFunction]) -> List[Dict[str, str]]:
    dropdown_options = []
    for key, item in function_dict.items():
        doc = inspect.getdoc(item)
        if doc is None or not is_function_typed(item):
            continue
        match = re.search(r"(.+?)\n", doc)
        if not match:
            raise DocError(f"Invalid name of function {key} for UI")
        name = match.group(1)
        dropdown_options.append({"label": name, "value": key})
    return dropdown_options


def is_function_typed(function: GraphFunction) -> bool:
    sig = inspect.signature(function)
    if sig.return_annotation == inspect.Parameter.empty:
        return False
    for _, value in sig.parameters.items():
        if value.annotation == inspect.Parameter.empty:
            return False
    return True


# proxy_wrapper_map = {
#     Output("graph-cytoscape", "elements"): lambda proxy: cyto.Cytoscape(
#         id="graph-cytoscape",
#         elements=proxy,
#         style={"width": "100%", "height": "600px"},
#         layout={"name": "circle"},
#         autoRefreshLayout=True,
#     ), Output("modal", "is_open"): lambda proxy: dbc.Modal(
#             [
#                 dbc.ModalHeader("Graph Templates"),
#                 dbc.ModalBody(children=graph_templates),
#                 dbc.ModalFooter(
#                     dbc.Button("CLOSE BUTTON", id="close", className="ml-auto")
#                 ),
#             ],
#             id="modal", is_open=proxy
#         )
# }
# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    transforms=[MultiplexerTransform()],
    suppress_callback_exceptions=True,
)

add_attrs = "additional_attributes"
input_stylesheet = {
    "display": "flex",
    "flex-direction": "column",
    "align-items": "center",
}

graph_templates = html.Div(
    [
        dcc.Dropdown(
            options=dropdown_functions(function_dict),
            id="graph_layout_dropdown",
            value=None,
        ),
        html.Div(id="input_fields", style=input_stylesheet),
    ],
    id="modal_html_body",
)

sidebar_style = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "4rem 1rem 2rem",
    "background-color": "#f8f9fa",
}

content_style = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar_container = html.Div(
    children=[],
    id="sidebar_container",
)

graphxdd = nx.Graph()

test_elements2 = [{"data": {"id": "center", "label": "center", "add_data": False}}]

app.layout = html.Div(
    id="app-window",
    children=[
        cyto.Cytoscape(
            id="graph-cytoscape",
            elements=test_elements2,
            style={"width": "100%", "height": "700px"},
            layout={"name": "preset"},
            autoRefreshLayout=True,
            boxSelectionEnabled=True,
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
                    dbc.Button(
                        "Generate Graph from Template",
                        id="graph_generate_button",
                        className="ml-auto",
                    )
                ),
            ],
            id="modal",
        ),
        html.Div(id="output-data-upload"),
        html.Div(id="position_click"),
        sidebar_container,
    ],
    tabIndex="0",
    style={"outline": None},
)


def handle_yaml_graph(networkx_data: Dict) -> GraphOrNone:
    networkx_data = networkx_data.get("graph_params", None)
    if networkx_data is None:
        print("Bad yaml file")
        return None
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


def call_graph_function_with_params(
    func_reference: GraphFunction, param_dict: Dict[str, Any]
) -> Graph:
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
    Output("input_fields", "children"),
    [Input("graph_layout_dropdown", "value")],
    prevent_initial_call=True,
)
def create_input_fields(selected_option: str) -> List[InputComponent]:
    # using global variable
    input_fields = []
    if selected_option is None:
        return input_fields
    selected_function = function_dict[selected_option]
    doc = inspect.getdoc(selected_function)
    pattern = r"\s*([\w\s]+\w)\s*-\s*(\w+)\s*:\s*(.+)"
    parameters = re.findall(pattern, doc, flags=re.MULTILINE)
    for parameter in parameters:
        input_fields.append(html.Label(parameter[0], className="label"))
        type_annotation = (
            inspect.signature(selected_function).parameters[parameter[1]].annotation
        )
        input_fields.append(
            create_function_parameter_input_field(
                parameter[1], type_annotation, parameter[2], selected_function
            )
        )
    return input_fields


def create_function_parameter_input_field(
    parameter_name: str,
    parameter_type: Type,
    parameter_desc: str,
    function: GraphFunction,
) -> InputComponent:
    params = inspect.signature(function).parameters
    required = params[parameter_name].default is inspect.Parameter.empty
    default = None
    if not required:
        default = params[parameter_name].default

    if (
        parameter_type == int
        or parameter_type == float
        or parameter_type == Optional[int]
    ):
        return dcc.Input(
            id=parameter_name,
            type="number",
            min=0,
            required=required,
            value=default,
            className="input",
        )
    elif parameter_type == bool:
        if default is None:
            return daq.BooleanSwitch(id=parameter_name, on=False, className="input")
        return daq.BooleanSwitch(id=parameter_name, on=default)
    elif (
        parameter_type == dict
        or parameter_type == Optional[dict]
        or parameter_type == Optional[list]
        or parameter_type == list
    ):
        return dcc.Input(
            id=parameter_name,
            type="text",
            required=required,
            value=str(default),
            className="label",
        )
    else:
        return html.Label("Unknown parameter type in function")


@app.callback(
    Output("sidebar_container", "children"),
    [
        Input("graph-cytoscape", "selectedNodeData"),
        Input("graph-cytoscape", "selectedEdgeData"),
        State("graph-cytoscape", "elements"),
    ],
)
def create_attribute_input_fields(selected_nodes, selected_edges, elements):
    selected_nodes, selected_edges = optional_none_to_empty_list(
        selected_nodes
    ), optional_none_to_empty_list(selected_edges)
    selected_nodes_edges = selected_nodes + selected_edges
    if len(selected_nodes_edges) == 0:
        return []
    sidebar_children = []
    attributes = []
    additional_attrs = []
    for selected_item in selected_nodes_edges:
        additional_attr = selected_item[add_attrs]
        attributes.append(extract_attribute_names(additional_attr))
        additional_attrs.append(additional_attr)
    common_attr = list(reduce(set.intersection, attributes))
    selected_items.set_attrs(common_attr)
    selected_items.set_elements(selected_nodes_edges)
    selected_items.set_nodes(selected_nodes)
    selected_items.set_edges(selected_edges)
    selected_items.generate_selected_elements_idxs(elements)
    for attr in common_attr:
        number_of_values = count_unique_values(additional_attrs, attr)
        sidebar_children += create_attribute_input_field(
            additional_attrs, number_of_values, attr
        )
    sidebar_children.append(html.Button("Confirm Edit", id="confirm-edit-button"))
    sidebar_children.append(
        html.Button("Add Attribute", id="add-attribute-button", disabled=True)
    )
    sidebar_children.append(
        dcc.Dropdown(
            ["Number", "Boolean", "Text", "Dictionary"],
            placeholder="Select Attribute Value Type",
            id="attribute-type-dropdown",
        )
    )
    sidebar_children.append(
        html.Button("Remove Attribute", id="remove-attribute-button", disabled=True)
    )
    sidebar_children.append(
        dcc.Dropdown(
            common_attr,
            placeholder="Select Attribute to Remove",
            id="remove-attribute-dropdown",
        )
    )
    sidebar_children.append(
        dcc.Input(id="add-attribute-name", type="text", placeholder="Attribute Name")
    )
    sidebar_children.append(html.Div(id="add-attribute-value-container"))
    sidebar = html.Div(
        id="sidebar_div",
        children=sidebar_children,
        style=sidebar_style,
    )
    return sidebar


def optional_none_to_empty_list(optional_list):
    if optional_list is None:
        return []
    return optional_list


def extract_attribute_names(selected_item):
    return set(selected_item.keys())


def count_unique_values(values, key):
    return len(set(value[key] for value in values))


def create_attribute_input_field(additional_attrs, value_count, key):
    input_fields = []
    first_dict = additional_attrs[0]
    input_fields.append(create_attribute_name_input_field(key))
    if value_count == 1:
        input_value = first_dict[key]
        input_fields.append(create_attribute_value_input_field(input_value, key))
        return input_fields
    input_fields.append(html.Label("Value count: " + str(value_count)))
    return input_fields


def create_attribute_value_input_field(input_value, attr_name):
    dict_id = ""
    if isinstance(input_value, bool):
        return daq.BooleanSwitch(id="value_" + attr_name, on=input_value)
    if isinstance(input_value, str) or isinstance(input_value, dict):
        dict_id = dict_id_addition(input_value)
        input_type = "text"
        input_value = str(input_value)
    else:
        input_type = "number"
    return dcc.Input(
        value=input_value, id=dict_id + "value_" + attr_name, type=input_type
    )


def create_attribute_name_input_field(attr_name):
    return dcc.Input(value=attr_name, type="text", id="key_" + attr_name)


def dict_id_addition(value):
    if isinstance(value, dict):
        return "dict_"
    return "text_"


@app.callback(
    [
        Output("add-attribute-value-container", "children"),
        Output("add-attribute-button", "disabled"),
    ],
    [
        Input("attribute-type-dropdown", "value"),
        Input("add-attribute-name", "value"),
        State("add-attribute-value-container", "children"),
    ],
    prevent_initial_call=True,
)
def set_attribute_value_input_type(dropdown_value, attribute_name, container_children):
    if dropdown_value is None:
        return [], True
    disabled = attribute_name is None or attribute_name == ""
    if (
        container_children is not None
        and len(container_children) > 0
        and is_right_input_type(dropdown_value, container_children)
    ):
        return container_children, disabled
    if dropdown_value == "Boolean":
        input_field = daq.BooleanSwitch(
            id="add-attribute-value", on=False, label="Attribute Value"
        )
    elif dropdown_value == "Number":
        input_field = dcc.Input(
            id="add-attribute-value", type="number", placeholder="Attribute Value"
        )
    else:
        input_field = dcc.Input(
            id="add-attribute-value", type="text", placeholder="Attribute Value"
        )
    return input_field, disabled


def is_right_input_type(dropdown_value, container_children):
    return (
        dropdown_value == "Boolean"
        and container_children["type"] == "BooleanSwitch"
        or (
            container_children["type"] == "Input"
            and (
                dropdown_value == "Number"
                and container_children["props"]["type"] == "number"
                or (dropdown_value == "Text" or dropdown_value == "Dict")
                and container_children["props"]["type"] == "text"
            )
        )
    )


@app.callback(
    Output("remove-attribute-button", "disabled"),
    Input("remove-attribute-dropdown", "value"),
)
def remove_button_disabler(dropdown_value):
    return dropdown_value is None or dropdown_value == ""


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("remove-attribute-dropdown", "options"),
    ],
    [
        Input("confirm-edit-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
    ],
    prevent_initial_call=True,
)
def confirm_button_click(n_clicks, sidebar_children, elements, dropdown_options):
    if (
        n_clicks is None
        or n_clicks < 1
        or len(sidebar_children) == 0
        or sidebar_children[0]["props"]["id"] == "confirm-edit-button"
    ):
        return elements, dropdown_options
    start_idx = 0
    elements_idxs = selected_items.get_elements_idxs()
    common_attrs = selected_items.get_attrs()
    new_common_attrs = common_attrs.copy()
    for element_idx in elements_idxs:
        update_element_attributes_sidebar(
            start_idx,
            sidebar_children,
            element_idx,
            elements,
            common_attrs,
            new_common_attrs,
        )
    selected_items.set_attrs(new_common_attrs)
    return elements, new_common_attrs


def update_element_attributes_sidebar(
    start_idx, sidebar_children, element_idx, elements, common_attrs, new_common_attrs
):
    for name_input_idx in range(start_idx, len(sidebar_children), 2):
        if is_confirm_edit_button(sidebar_children, name_input_idx):
            break
        common_attr_idx = (name_input_idx - start_idx) // 2
        value_input_idx = name_input_idx + 1
        old_name = common_attrs[common_attr_idx]
        new_name = sidebar_children[name_input_idx]["props"]["value"]
        update_element_value_sidebar(
            sidebar_children, value_input_idx, elements, element_idx, old_name
        )
        elements[element_idx]["data"][add_attrs][new_name] = elements[element_idx][
            "data"
        ][add_attrs].pop(old_name)
        new_common_attrs[common_attr_idx] = new_name


def update_element_value_sidebar(
    sidebar_children, value_input_idx, elements, element_idx, attr_name
):
    if sidebar_children[value_input_idx]["type"] == "Label":
        return
    value = extract_value_from_children(sidebar_children, value_input_idx)
    elements[element_idx]["data"][add_attrs][attr_name] = value


def is_confirm_edit_button(sidebar_children, idx):
    return sidebar_children[idx]["props"].get("id", "") == "confirm-edit-button"


def extract_value_from_children(children, value_input_idx=None, dropdown_value=""):
    if value_input_idx is None:
        if children["type"] == "Input" and (
            children["props"]["id"][:5] == "dict_" or dropdown_value == "Dictionary"
        ):
            value = json.loads(children["props"]["value"])
        elif children["type"] == "Input":
            value = children["props"]["value"]
        else:
            value = children["props"]["on"]
    else:
        if children[value_input_idx]["type"] == "Input" and (
            children[value_input_idx]["props"]["id"][:5] == "dict_"
            or dropdown_value == "Dictionary"
        ):
            value = json.loads(children[value_input_idx]["props"]["value"])
        elif children[value_input_idx]["type"] == "Input":
            value = children[value_input_idx]["props"]["value"]
        else:
            value = children[value_input_idx]["props"]["on"]
    return value


@app.callback(
    [Output("graph-cytoscape", "elements"), Output("sidebar_div", "children")],
    [
        Input("add-attribute-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("add-attribute-name", "value"),
        State("add-attribute-value-container", "children"),
        State("attribute-type-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def add_button_click(
    n_clicks,
    sidebar_children,
    elements,
    dropdown_options,
    new_attribute_name,
    attr_val_container_children,
    type_dropdown_value,
):
    if (
        n_clicks is None
        or n_clicks < 1
        or new_attribute_name is None
        or new_attribute_name == ""
        or attr_val_container_children is None
        or len(attr_val_container_children) == 0
    ):
        return elements, sidebar_children
    new_attribute_value = extract_value_from_children(
        attr_val_container_children, dropdown_value=type_dropdown_value
    )
    elements_idxs = selected_items.get_elements_idxs()
    for element_idx in elements_idxs:
        elements[element_idx]["data"][add_attrs][
            new_attribute_name
        ] = new_attribute_value
    common_attrs = selected_items.get_attrs()
    common_attrs.append(new_attribute_name)
    selected_items.set_attrs(common_attrs)
    dropdown_options.append(new_attribute_name)
    insert_idx = 0
    for i in range(len(sidebar_children)):
        if is_confirm_edit_button(sidebar_children, i):
            insert_idx = i
    sidebar_children[insert_idx + 4]["props"]["options"] = dropdown_options
    sidebar_children[len(sidebar_children) - 2]["props"]["value"] = ""
    sidebar_children[insert_idx + 1]["props"]["disabled"] = True
    sidebar_children.insert(
        insert_idx,
        create_attribute_value_input_field(new_attribute_value, new_attribute_name),
    )
    sidebar_children.insert(
        insert_idx, create_attribute_name_input_field(new_attribute_name)
    )
    return elements, sidebar_children


@app.callback(
    [Output("graph-cytoscape", "elements"), Output("sidebar_div", "children")],
    [
        Input("remove-attribute-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("remove-attribute-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def remove_button_click(
    n_clicks, sidebar_children, elements, remove_options, remove_value
):
    if n_clicks is None or n_clicks < 1 or remove_value is None or remove_value == "":
        return elements, sidebar_children
    elements_idxs = selected_items.get_elements_idxs()
    for element_idx in elements_idxs:
        elements[element_idx]["data"][add_attrs].pop(remove_value)
    common_attrs = selected_items.get_attrs()
    remove_options.remove(remove_value)
    first_input_idx = -1
    for i in range(len(sidebar_children)):
        if sidebar_children[i]["type"] == "Input" and first_input_idx == -1:
            first_input_idx = i
        if is_confirm_edit_button(sidebar_children, i):
            confirm_idx = i
            break
    remove_dropdown_idx = confirm_idx + 4
    sidebar_children[remove_dropdown_idx]["props"]["options"] = remove_options
    sidebar_children[remove_dropdown_idx]["props"]["value"] = ""
    sidebar_children[confirm_idx + 3]["props"]["disabled"] = True
    for i in range(len(common_attrs)):
        if common_attrs[i] == remove_value:
            rem_attr_idx = i
            break
    sidebar_children.pop(first_input_idx + 2 * rem_attr_idx + 1)
    sidebar_children.pop(first_input_idx + 2 * rem_attr_idx)
    common_attrs.remove(remove_value)
    selected_items.set_attrs(common_attrs)
    return elements, sidebar_children


@app.callback(
    [Output("graph-cytoscape", "elements"), Output("modal", "is_open")],
    [Input("graph_generate_button", "n_clicks")],
    [State("graph_layout_dropdown", "value"), State("input_fields", "children")],
    prevent_initial_call=True,
)
def button_click(
    n_clicks: int, value: str, html_input_children: List[InputComponent]
) -> Tuple[GraphElements, bool]:
    print(html_input_children)
    if n_clicks is None or html_input_children is None:
        return [], False
    param_dict = {}
    for child in html_input_children:
        if child["type"] == "Label":
            continue
        param_name, param_value = handle_input_dict(child)
        param_dict[param_name] = param_value
    graph = call_graph_function_with_params(function_dict[value], param_dict)
    return convert_networkx_to_cytoscape(graph), False


def handle_input_dict(input_dict):
    if input_dict["type"] == "BooleanSwitch":
        value = input_dict["props"]["on"]
    elif input_dict["props"]["type"] == "number":
        value = input_dict["props"]["value"]
    else:
        value = ast.literal_eval(input_dict["props"]["value"])
    name = input_dict["props"]["id"]
    return name, value


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
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


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "ehcompleteSource"),
        Input("graph-cytoscape", "ehcompleteTarget"),
        State("graph-cytoscape", "elements"),
    ],
)
def rebind_new_edge(source, target, elements):
    if source is None or target is None:
        return elements
    new_edge = {
        "data": {"source": source["id"], "target": target["id"], add_attrs: dict()}
    }
    elements.append(new_edge)
    return elements


def convert_networkx_to_cytoscape(graph: nx.Graph):
    x_idx = 0
    y_idx = 1
    scaling_factor = 500
    cyto_nodes = []
    positions = nx.spring_layout(graph)
    id_generator.reset()
    for node in graph.nodes():
        # Get the node attributes from the NetworkX graph
        node_attrs = graph.nodes[node]
        id_generator.increment_id()

        # Create a dictionary representing the Cytoscape node with the modified attributes
        cyto_node = {
            "data": {"id": str(node), "label": str(node), add_attrs: node_attrs},
            "position": {
                "x": positions[node][x_idx] * scaling_factor,
                "y": positions[node][y_idx] * scaling_factor,
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
                add_attrs: edge_attrs,
            }
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
                key: value for key, value in element["data"][add_attrs].items()
            }
            nx_graph.add_node(node_id, **node_attrs)
        else:
            # This element is an edge
            source_id = element["data"]["source"]
            target_id = element["data"]["target"]
            edge_attrs = {
                key: value for key, value in element["data"][add_attrs].items()
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
                key: value for key, value in element["data"][add_attrs].items()
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
        for key, value in element["data"][add_attrs].items()
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
        State("graph-cytoscape", "selectedNodeData"),
        State("graph-cytoscape", "selectedEdgeData"),
    ],
)
def test_graph(n, elements, node_data, edge_data):
    if n:
        print(elements)
        print("\n")
        print(node_data)
        print("\n")
        print(edge_data)
        return "Klik"
    return "Neklik"


@app.callback(
    Output("position_click", "children"),
    Input("graph-cytoscape", "tapData"),
)
def test_click(node_data):
    print("\n")
    print(node_data)
    return "Pozice kliknuti"


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "dblTapData"),
        State("graph-cytoscape", "elements"),
    ],
)
def add_node(pos, elements):
    if pos is None:
        return elements
    node_id = id_generator.generate_id()
    new_node = {
        "data": {"id": node_id, "label": node_id, add_attrs: dict()},
        "position": {"x": pos["x"], "y": pos["y"]},
    }
    elements.append(new_node)
    return elements


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "dblTapNode"),
        State("graph-cytoscape", "elements"),
    ],
)
def delete_node(node, elements):
    if node is None:
        return elements
    node_id = node["data"]["id"]
    edges = node["edgesData"]
    for element in elements:
        if (
            is_node(element)
            and element["data"]["id"] == node_id
            or not is_node(element)
            and is_removable_edge(element, edges)
        ):
            elements.remove(element)
    return elements


def is_removable_edge(edge, removable_edges):
    for removable_edge in removable_edges:
        if removable_edge == edge:
            return True
    return False


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "dblTapEdge"),
        State("graph-cytoscape", "elements"),
    ],
)
def delete_edge(edge, elements):
    if edge is None:
        return elements
    source_id = edge["sourceData"]["id"]
    target_id = edge["targetData"]["id"]
    for element in elements:
        if (
            not is_node(element)
            and element["data"]["source"] == source_id
            and element["data"]["target"] == target_id
        ):
            elements.remove(element)
    return elements


if __name__ == "__main__":
    app.run_server(debug=True)
