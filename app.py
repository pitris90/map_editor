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
from typing import Callable, Any, Union, Optional, Tuple, Type
from type_aliases import (
    Graph,
    GraphFunction,
    GraphOrNone,
    GraphElements,
    GraphElement,
    InputComponent,
    InputValue,
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
        self._selected_common_attrs: list = []
        self._selected_elements: GraphElements = []
        self._selected_edges: GraphElements = []
        self._selected_nodes: GraphElements = []
        self._selected_elements_idxs: list = []

    def set_attrs(self, selected_common_attrs: list) -> None:
        self._selected_common_attrs = selected_common_attrs

    def get_attrs(self) -> list:
        return self._selected_common_attrs.copy()

    def set_elements(self, selected_elements: GraphElements) -> None:
        self._selected_elements = selected_elements

    def get_elements(self) -> GraphElements:
        return self._selected_elements.copy()

    def set_edges(self, selected_edges: GraphElements) -> None:
        self._selected_edges = selected_edges

    def get_edges(self) -> GraphElements:
        return self._selected_edges.copy()

    def set_nodes(self, selected_nodes: GraphElements) -> None:
        self._selected_nodes = selected_nodes

    def get_nodes(self) -> GraphElements:
        return self._selected_nodes.copy()

    def generate_selected_elements_idxs(self, elements: GraphElements) -> None:
        selected_elements_idxs: list = []
        for i in range(0, len(elements)):
            self._append_idx_if_selected_element(elements, i, selected_elements_idxs)
        self._selected_elements_idxs = selected_elements_idxs

    def _append_idx_if_selected_element(
        self, elements: GraphElements, element_idx: int, selected_elements_idxs: list
    ) -> None:
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

    def get_elements_idxs(self) -> list:
        return self._selected_elements_idxs


# get the absolute path of the current directory
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
FOLDER_NAME = "graph_templates"
# join the current directory with the folder name
DIRECTORY = os.path.join(CURRENT_DIR, FOLDER_NAME)
sys.path.append(DIRECTORY)
FUNCTION_DICT = {}
selected_items = Selected_items()
id_generator = Id_generator()

for filename in os.listdir(DIRECTORY):
    if os.path.isfile(os.path.join(DIRECTORY, filename)) and filename.endswith(".py"):
        module_name = filename[:-3]  # remove the .py extension
        module = importlib.import_module(module_name)
        function = getattr(module, module_name)
        FUNCTION_DICT[module_name] = function


def dropdown_functions(function_dict: dict[str, GraphFunction]) -> list[dict[str, str]]:
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

ADD_ATTRS = "additional_attributes"
INPUT_STYLESHEET = {
    "display": "flex",
    "flex-direction": "column",
    "align-items": "center",
}

GRAPH_TEMPLATES = html.Div(
    [
        dcc.Dropdown(
            options=dropdown_functions(FUNCTION_DICT),
            id="graph_layout_dropdown",
            value=None,
        ),
        html.Div(id="input_fields", style=INPUT_STYLESHEET),
    ],
    id="modal_html_body",
)

ATTRIBUTE_SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "4rem 1rem 2rem",
    "background-color": "#f8f9fa",
}

CONTROLS_SIDEBAR_STYLE = {
    # "position": "fixed",
    # "top": 0,
    # "right": 0,
    # "bottom": 0,
    "display": "flex",
    "flex-direction": "column",
    "width": "250px",
    "padding": "2rem",
    "background-color": "gray",
    "flex-shrink": 0,
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

ROOT_DIV_STYLE = {"display": "flex", "outline": None, "height": "100vh"}

ATTRIBUTE_SIDEBAR_CONTAINER = html.Div(
    children=[],
    id="sidebar_container",
)

# test_elements2 = [{"data": {"id": "center", "label": "center", "add_data": False}}]

app.layout = html.Div(
    id="app-window",
    children=[
        html.Div(
            children=[
                dbc.Button("New Graph", id="new-graph-button", class_name="mb-2"),
                dcc.Upload(
                    id="upload-graph",
                    children=dbc.Button("Upload Graph", class_name="mb-2 w-100"),
                ),
                dcc.Download(id="save-graph"),
                dbc.Button("Download Graph", id="save-graph-image", class_name="mb-2"),
                dbc.Button("Graph Template Functions", id="open", class_name="mb-2"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Graph Templates"),
                        dbc.ModalBody(children=GRAPH_TEMPLATES),
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
                daq.BooleanSwitch(
                    on=False,
                    id="orientation-graph-switcher",
                    label="Undirected",
                    className="mb-2",
                ),
            ],
            style=CONTROLS_SIDEBAR_STYLE,
        ),
        cyto.Cytoscape(
            id="graph-cytoscape",
            elements=[],
            style={"width": "100%", "height": "100%", "flex": 1},
            stylesheet=[
                {
                    "selector": "edge",
                    "style": {
                        "curve-style": "bezier",
                        "target-arrow-shape": "none",
                    },
                },
                {
                    "selector": "node",
                    "style": {
                        "label": "data(label)",
                    },
                },
            ],
            layout={
                "name": "preset"
                # "boundingBox": {"x1": 0, "y1": 0, "x2": 4294967295, "y2": 4294967295},
            },
            autoRefreshLayout=True,
            boxSelectionEnabled=True,
        ),
        # html.Button("Debug Button", id="main-debug-button"),
        # html.Div(id="output-data-upload"),
        # html.Div(id="position_click"),
        ATTRIBUTE_SIDEBAR_CONTAINER,
    ],
    tabIndex="0",
    style=ROOT_DIV_STYLE,
)


def handle_yaml_graph(networkx_data: dict) -> GraphOrNone:
    networkx_data = networkx_data.get("graph_params", None)
    if networkx_data is None:
        print("Bad yaml file")
        return None
    if networkx_data.get("loader") == "hardcodedxx":
        # different handling
        return networkx_data
    loader_function = FUNCTION_DICT[networkx_data["loader"]]
    print(inspect.signature(loader_function).parameters)
    print(networkx_data["loader_params"])
    graph = call_graph_function_with_params(
        loader_function, networkx_data["loader_params"]
    )
    return graph


def call_graph_function_with_params(
    func_reference: GraphFunction, param_dict: dict[str, Any]
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
        return dbc.Input(
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
        return dbc.Input(
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
def create_attribute_input_fields(
    selected_nodes: GraphElements,
    selected_edges: GraphElements,
    elements: GraphElements,
) -> html.Div:
    selected_nodes, selected_edges = optional_none_to_empty_list(
        selected_nodes
    ), optional_none_to_empty_list(selected_edges)
    selected_nodes_edges = selected_nodes + selected_edges
    if len(selected_nodes_edges) == 0:
        return []
    sidebar_children = []
    attributes: list = []
    additional_attrs = []
    for selected_item in selected_nodes_edges:
        additional_attr = selected_item[ADD_ATTRS]
        attributes.append(extract_attribute_names(additional_attr))
        additional_attrs.append(additional_attr)
    common_attr = list(reduce(set.intersection, attributes))  # type: ignore
    selected_items.set_attrs(common_attr)
    selected_items.set_elements(selected_nodes_edges)
    selected_items.set_nodes(selected_nodes)
    selected_items.set_edges(selected_edges)
    selected_items.generate_selected_elements_idxs(elements)
    sidebar_children.append(
        html.H4("Graph Element's Properties Editor", id="graph_prop_editor_heading")
    )
    if len(selected_nodes) == 1 and len(selected_edges) == 0:
        sidebar_children.append(html.H5("Node's Label", id="node_label_field_heading"))
        sidebar_children.append(
            dbc.Input(
                value=selected_nodes[0]["label"],
                type="text",
                id="node_label_field",
                class_name="w-100 d-inline-block mt-1 mb-4",
            )
        )
    sidebar_children.append(
        html.H5("Element's Attributes", id="elements_prop_fields_heading")
    )
    for attr in common_attr:
        number_of_values = count_unique_values(additional_attrs, attr)
        sidebar_children += create_attribute_input_field(
            additional_attrs, number_of_values, attr
        )
    sidebar_children.append(
        dbc.Button(
            "Confirm Edit",
            id="confirm-edit-button",
            class_name="w-100 mt-2 mb-2",
            color="info",
        )
    )
    sidebar_children.append(
        dcc.Dropdown(
            common_attr,
            placeholder="Select Attribute to Remove",
            id="remove-attribute-dropdown",
            className="w-100 mt-2 mb-1",
        )
    )
    sidebar_children.append(
        dbc.Button(
            "Remove Attribute",
            id="remove-attribute-button",
            disabled=True,
            class_name="w-100 mt-1 mb-2",
            color="danger",
        )
    )
    sidebar_children.append(
        dcc.Dropdown(
            ["Number", "Boolean", "Text", "Dictionary"],
            placeholder="Select Attribute Value Type",
            id="attribute-type-dropdown",
            className="mt-2 mb-1",
        )
    )
    sidebar_children.append(
        dbc.Input(
            id="add-attribute-name",
            type="text",
            placeholder="Attribute Name",
            class_name="mt-1 mb-1",
        )
    )
    sidebar_children.append(
        html.Div(id="add-attribute-value-container", className="mt-1 mb-1")
    )
    sidebar_children.append(
        dbc.Button(
            "Add Attribute",
            id="add-attribute-button",
            disabled=True,
            class_name="w-100 mt-1 mb-1",
            color="success",
        )
    )

    sidebar = html.Div(
        id="sidebar_div",
        children=sidebar_children,
        style=ATTRIBUTE_SIDEBAR_STYLE,
    )
    return sidebar


def optional_none_to_empty_list(optional_list: Optional[list]) -> list:
    if optional_list is None:
        return []
    return optional_list


def extract_attribute_names(selected_item: dict) -> set:
    return set(selected_item.keys())


def count_unique_values(values: list[dict], key: str) -> int:
    unique_set = set()
    for value in values:
        dict_value = value[key]
        if isinstance(dict_value, dict):
            dict_value = json.dumps(dict_value, sort_keys=True)
        unique_set.add(dict_value)
    return len(unique_set)
    # return len(set(value[key] for value in values))


def create_attribute_input_field(
    additional_attrs: list[dict], value_count: int, key: str
) -> list:
    input_fields = []
    first_dict = additional_attrs[0]
    input_fields.append(create_attribute_name_input_field(key))
    if value_count == 1:
        input_value = first_dict[key]
        input_fields.append(create_attribute_value_input_field(input_value, key))
        return input_fields
    input_fields.append(
        html.Label(
            "Value count: " + str(value_count),
            className="w-50 d-inline-block mt-1 mb-1",
        )
    )
    return input_fields


def create_attribute_value_input_field(
    input_value: InputValue, attr_name: str
) -> InputComponent:
    dict_id = ""
    if isinstance(input_value, bool):
        return daq.BooleanSwitch(
            id="value_" + attr_name,
            on=input_value,
            className="w-50 d-inline-block mt-1 mb-1",
        )
    if isinstance(input_value, str) or isinstance(input_value, dict):
        dict_id = dict_id_addition(input_value)
        input_type = "text"
        input_value = str(input_value)
    else:
        input_type = "number"
    return dbc.Input(
        value=input_value,
        id=dict_id + "value_" + attr_name,
        type=input_type,
        class_name="w-50 d-inline-block mt-1 mb-1",
    )


def create_attribute_name_input_field(attr_name: str) -> InputComponent:
    return dbc.Input(
        value=attr_name,
        type="text",
        id="key_" + attr_name,
        class_name="w-50 d-inline-block mt-1 mb-1",
    )


def dict_id_addition(value: Union[str, dict]) -> str:
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
def set_attribute_value_input_type(
    dropdown_value: Optional[str],
    attribute_name: Optional[str],
    container_children: Optional[InputComponent],
) -> tuple[InputComponent, bool]:
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
        input_field = dbc.Input(
            id="add-attribute-value", type="number", placeholder="Attribute Value"
        )
    else:
        input_field = dbc.Input(
            id="add-attribute-value", type="text", placeholder="Attribute Value"
        )
    return input_field, disabled


def is_right_input_type(
    dropdown_value: str, container_children: InputComponent
) -> bool:
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
def remove_button_disabler(dropdown_value: Optional[str]) -> bool:
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
def confirm_button_click(
    n_clicks: Optional[int],
    sidebar_children: list[InputComponent],
    elements: GraphElements,
    dropdown_options: Optional[list],
) -> tuple[GraphElements, Optional[list]]:
    if (
        n_clicks is None
        or n_clicks < 1
        or len(sidebar_children) == 0
        or sidebar_children[0]["props"]["id"] == "confirm-edit-button"
    ):
        return elements, dropdown_options
    ATTRIBUTE_INPUT_FIELDS_START_IDX = get_attribute_input_field_start(sidebar_children)
    elements_idxs = selected_items.get_elements_idxs()
    common_attrs = selected_items.get_attrs()
    selected_nodes = selected_items.get_nodes()
    selected_edges = selected_items.get_edges()
    if len(selected_nodes) == 1 and len(selected_edges) == 0:
        NODE_LABEL_FIELD_IDX = 2
        elements[elements_idxs[0]]["data"]["label"] = sidebar_children[
            NODE_LABEL_FIELD_IDX
        ]["props"]["value"]
    new_common_attrs = common_attrs.copy()
    for element_idx in elements_idxs:
        update_element_attributes_sidebar(
            ATTRIBUTE_INPUT_FIELDS_START_IDX,
            sidebar_children,
            element_idx,
            elements,
            common_attrs,
            new_common_attrs,
        )
    selected_items.set_attrs(new_common_attrs)
    return elements, new_common_attrs


def get_attribute_input_field_start(sidebar_children: list[InputComponent]) -> int:
    for element_idx in range(len(sidebar_children)):
        if (
            sidebar_children[element_idx]["props"]["id"]
            == "elements_prop_fields_heading"
        ):
            return element_idx + 1
    return -1


def update_element_attributes_sidebar(
    start_idx: int,
    sidebar_children: list[InputComponent],
    element_idx: int,
    elements: GraphElements,
    common_attrs: list,
    new_common_attrs: list,
) -> None:
    # iterating through attribute input fields
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
        elements[element_idx]["data"][ADD_ATTRS][new_name] = elements[element_idx][
            "data"
        ][ADD_ATTRS].pop(old_name)
        new_common_attrs[common_attr_idx] = new_name


def update_element_value_sidebar(
    sidebar_children: list[InputComponent],
    value_input_idx: int,
    elements: GraphElements,
    element_idx: int,
    attr_name: str,
) -> None:
    if sidebar_children[value_input_idx]["type"] == "Label":
        return
    value = extract_value_from_children(sidebar_children, value_input_idx)
    elements[element_idx]["data"][ADD_ATTRS][attr_name] = value


def is_confirm_edit_button(
    sidebar_children: list[InputComponent], idx: int
) -> InputComponent:
    return sidebar_children[idx]["props"].get("id", "") == "confirm-edit-button"


def extract_value_from_children(
    children: Union[list[dict], dict],
    value_input_idx: int = 0,
    dropdown_value: str = "",
) -> InputValue:
    if isinstance(children, dict):
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
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
    dropdown_options: list,
    new_attribute_name: Optional[str],
    attr_val_container_children: Optional[list],
    type_dropdown_value: str,
) -> tuple[GraphElements, list]:
    if (
        n_clicks is None
        or n_clicks < 1
        or new_attribute_name is None
        or new_attribute_name == ""
        or attr_val_container_children is None
        or len(attr_val_container_children) == 0
    ):
        return elements, sidebar_children
    REMOVE_DROPDOWN_OFFSET_FROM_CONFIRM = 1
    NEW_ATTRIBUTE_FIELD_NAME_OFFSET = 4
    ADD_ATTRIBUTE_BUTTON_OFFSET = 6
    new_attribute_value = extract_value_from_children(
        attr_val_container_children, dropdown_value=type_dropdown_value
    )
    elements_idxs = selected_items.get_elements_idxs()
    for element_idx in elements_idxs:
        elements[element_idx]["data"][ADD_ATTRS][
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
    sidebar_children[insert_idx + REMOVE_DROPDOWN_OFFSET_FROM_CONFIRM]["props"][
        "options"
    ] = dropdown_options
    sidebar_children[insert_idx + NEW_ATTRIBUTE_FIELD_NAME_OFFSET]["props"][
        "value"
    ] = ""
    sidebar_children[insert_idx + ADD_ATTRIBUTE_BUTTON_OFFSET]["props"][
        "disabled"
    ] = True
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
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
    remove_options: list,
    remove_value: Optional[str],
) -> tuple[GraphElements, list]:
    if n_clicks is None or n_clicks < 1 or remove_value is None or remove_value == "":
        return elements, sidebar_children
    elements_idxs = selected_items.get_elements_idxs()
    for element_idx in elements_idxs:
        elements[element_idx]["data"][ADD_ATTRS].pop(remove_value)
    common_attrs = selected_items.get_attrs()
    remove_options.remove(remove_value)
    FIRST_ATTR_INPUT_IDX = get_attribute_input_field_start(sidebar_children)
    for i in range(len(sidebar_children)):
        if is_confirm_edit_button(sidebar_children, i):
            CONFIRM_IDX = i
            break
    REMOVE_DROPDOWN_OFFSET = 1
    REMOVE_DROPDOWN_IDX = CONFIRM_IDX + REMOVE_DROPDOWN_OFFSET
    REMOVE_BUTTON_OFFSET = 2
    REMOVED_ATTRIBUTE_VALUE_OFFSET_FROM_NAME = 1
    sidebar_children[REMOVE_DROPDOWN_IDX]["props"]["options"] = remove_options
    sidebar_children[REMOVE_DROPDOWN_IDX]["props"]["value"] = ""
    sidebar_children[CONFIRM_IDX + REMOVE_BUTTON_OFFSET]["props"]["disabled"] = True
    for i in range(len(common_attrs)):
        if common_attrs[i] == remove_value:
            ATTRIBUTE_NAME_TO_BE_DELETED_IDX = i
            break
    sidebar_children.pop(
        FIRST_ATTR_INPUT_IDX
        + 2 * ATTRIBUTE_NAME_TO_BE_DELETED_IDX
        + REMOVED_ATTRIBUTE_VALUE_OFFSET_FROM_NAME
    )
    sidebar_children.pop(FIRST_ATTR_INPUT_IDX + 2 * ATTRIBUTE_NAME_TO_BE_DELETED_IDX)
    common_attrs.remove(remove_value)
    selected_items.set_attrs(common_attrs)
    return elements, sidebar_children


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("modal", "is_open"),
        Output("orientation-graph-switcher", "on"),
        Output("orientation-graph-switcher", "label"),
        Output("graph-cytoscape", "stylesheet"),
    ],
    [
        Input("graph_generate_button", "n_clicks"),
        State("graph_layout_dropdown", "value"),
        State("input_fields", "children"),
        State("graph-cytoscape", "stylesheet"),
    ],
    prevent_initial_call=True,
)
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
        if child["type"] == "Label":
            continue
        param_name, param_value = handle_input_dict(child)
        param_dict[param_name] = param_value
    graph = call_graph_function_with_params(FUNCTION_DICT[value], param_dict)
    cytoscape_elements, directed = convert_networkx_to_cytoscape(graph)
    label, stylesheet = graph_orientation_switcher(directed, stylesheet)
    return cytoscape_elements, False, directed, label, stylesheet


def handle_input_dict(input_dict: dict) -> tuple[str, InputValue]:
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
def toggle_modal(n1: Optional[int], is_open: bool) -> bool:
    if n1:
        return not is_open
    return is_open


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
    cytoscape_graph = nx.cytoscape_data(graph)
    # convert the NetworkX data to a Cytoscape-compatible JSON format

    # return the Cytoscape-compatible JSON data

    # LEGACY TEST CODE
    # elements = (
    #     cytoscape_graph["elements"]["nodes"] + cytoscape_graph["elements"]["edges"]
    # )
    # xdelements = (
    #     cytoscape_graph["elements"]["nodes"] + cytoscape_graph["elements"]["edges"]
    # )
    elements, directed = convert_networkx_to_cytoscape(graph)
    label, stylesheet = graph_orientation_switcher(directed, stylesheet)
    # test_graph = convert_cytoscape_to_networkx(elements)
    return elements, directed, label, stylesheet


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "ehcompleteSource"),
        Input("graph-cytoscape", "ehcompleteTarget"),
        State("graph-cytoscape", "elements"),
        State("orientation-graph-switcher", "on"),
    ],
)
def rebind_new_edge(
    source: Optional[GraphElement],
    target: Optional[GraphElement],
    elements: GraphElements,
    directed: bool,
) -> GraphElements:
    if (
        source is None
        or target is None
        or not can_add_new_edge(source, target, elements, directed)
    ):
        return elements
    new_edge = {
        "data": {"source": source["id"], "target": target["id"], ADD_ATTRS: dict()}
    }
    elements.append(new_edge)
    return elements


def can_add_new_edge(
    source: GraphElement, target: GraphElement, elements: GraphElements, directed: bool
) -> bool:
    target_id = target["id"]
    source_id = source["id"]
    for element in elements:
        if is_node(element):
            continue
        element_source_id = element["data"]["source"]
        element_target_id = element["data"]["target"]
        same_edge = element_source_id == source_id and element_target_id == target_id
        if (
            directed
            and same_edge
            or not directed
            and (
                same_edge
                or element_source_id == target_id
                and element_target_id == source_id
            )
        ):
            return False
    return True


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
        if node_attrs.get("position", True) == True:
            position_x = positions[node][x_idx] * scaling_factor
            position_y = positions[node][y_idx] * scaling_factor
        else:
            position_x = node_attrs["position"]["x"]
            position_y = node_attrs["position"]["y"]
            node_attrs.pop("position")
        if node_attrs.get("label", True) == True:
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
    # temporary - now only converting to non directed graph settings
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


def is_node(element: GraphElement) -> bool:
    return "source" not in element["data"] and "target" not in element["data"]


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


@app.callback(
    Output("output-data-upload", "children"),
    [
        Input("main-debug-button", "n_clicks"),
        State("graph-cytoscape", "elements"),
        State("graph-cytoscape", "tapNode"),
        State("graph-cytoscape", "selectedNodeData"),
        State("graph-cytoscape", "selectedEdgeData"),
        State("graph-cytoscape", "stylesheet"),
        State("graph-cytoscape", "ele_move_pos"),
    ],
)
def test_graph(
    n: Optional[int],
    elements: GraphElements,
    tapNode: Any,
    node_data: list,
    edge_data: list,
    stylesheet: list,
    new_posiiton: Any,
) -> str:
    if n:
        print(elements)
        print("\n")
        print(node_data)
        print("\n")
        print(edge_data)
        return "Klik"
    return "Neklik"


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "ele_move_pos"),
        State("graph-cytoscape", "ele_move_data"),
        State("graph-cytoscape", "elements"),
        State("graph-cytoscape", "selectedNodeData"),
    ],
)
def update_positions(
    new_node_position: dict,
    moved_node_data: dict,
    elements: GraphElements,
    selected_node_data: Optional[list],
) -> GraphElements:
    element_edited = False
    for element in elements:
        if is_node(element) and element["data"]["id"] == moved_node_data["id"]:
            x_diff = new_node_position["x"] - element["position"]["x"]
            y_diff = new_node_position["y"] - element["position"]["y"]
            element["position"] = new_node_position
            element_edited = True
            break
    if selected_node_data is None or len(selected_node_data) == 0 or not element_edited:
        return elements
    for idx in selected_items.get_elements_idxs():
        if (
            is_node(elements[idx])
            and elements[idx]["data"]["id"] == moved_node_data["id"]
        ):
            continue
        if is_node(elements[idx]):
            elements[idx]["position"]["x"] += x_diff
            elements[idx]["position"]["y"] += y_diff
    return elements


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
    Output("position_click", "children"),
    Input("graph-cytoscape", "tapData"),
)
def test_click(node_data: dict) -> str:
    print("\n")
    print(node_data)
    return "Pozice kliknuti"


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


def edge_target_arrow_shape(directed: bool) -> str:
    if directed:
        return "triangle"
    return "none"


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "dblTapData"),
        State("graph-cytoscape", "elements"),
    ],
)
def add_node(pos: Optional[dict], elements: GraphElements) -> GraphElements:
    if pos is None:
        return elements
    node_id = id_generator.generate_id()
    new_node = {
        "data": {"id": node_id, "label": node_id, ADD_ATTRS: dict()},
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
def delete_node(node: Optional[GraphElement], elements: GraphElements) -> GraphElements:
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


def is_removable_edge(edge: GraphElement, removable_edges: GraphElements) -> bool:
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
def delete_edge(edge: Optional[GraphElement], elements: GraphElements) -> GraphElements:
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
    app.run_server(debug=False)
