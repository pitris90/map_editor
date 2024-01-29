from app import app
from dash_extensions.enrich import (  # type: ignore
    Output,
    Input,
    State,
    html,
    dcc,
)
from type_aliases import (
    GraphElements,
    InputComponent,
    InputValue,
)
from typing import Union, Optional
from graph_utils import ADD_ATTRS, is_node
import dash_bootstrap_components as dbc  # type: ignore
import dash_daq as daq  # type: ignore
import json
import ast
from functools import reduce
from css_stylesheets import ATTRIBUTE_SIDEBAR_STYLE


# Constants for indexing selected_items data
COMMON_ATTRS = 0
ELEMENTS = 1
EDGES = 2
NODES = 3
ELEMENTS_IDXS = 4


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

    def get_data(self) -> list:
        return [self._selected_common_attrs, self._selected_elements, self._selected_edges,
                self._selected_nodes, self._selected_elements_idxs]

    def set_data(self, data: list) -> None:
        self._selected_common_attrs = data[COMMON_ATTRS]
        self._selected_elements = data[ELEMENTS]
        self._selected_edges = data[EDGES]
        self._selected_nodes = data[NODES]
        self._selected_elements_idxs = data[ELEMENTS_IDXS]


# Helper functions for attribute editor
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
        if isinstance(dict_value, list) or isinstance(dict_value, set):
            dict_value = str(dict_value)
        unique_set.add(dict_value)
    return len(unique_set)


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
    evaluate_id = ""
    if isinstance(input_value, bool):
        return daq.BooleanSwitch(
            id="value_" + attr_name,
            on=input_value,
            className="w-50 d-inline-block mt-1 mb-1",
        )
    if (
        isinstance(input_value, str)
        or isinstance(input_value, dict)
        or isinstance(input_value, list)
        or isinstance(input_value, set)
    ):
        evaluate_id = evaluate_id_addition(input_value)
        input_type = "text"
        input_value = str(input_value)
    else:
        input_type = "number"
    return dbc.Input(
        value=input_value,
        id=evaluate_id + "value_" + attr_name,
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


def evaluate_id_addition(value: Union[str, dict]) -> str:
    if isinstance(value, dict) or isinstance(value, list) or isinstance(value, set):
        return "dict_"
    return "text_"


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
            value = ast.literal_eval(children["props"]["value"])
        elif children["type"] == "Input":
            value = children["props"]["value"]
        else:
            value = children["props"]["on"]
    else:
        if children[value_input_idx]["type"] == "Input" and (
            children[value_input_idx]["props"]["id"][:5] == "dict_"
            or dropdown_value == "Dictionary"
        ):
            value = ast.literal_eval(children[value_input_idx]["props"]["value"])
        elif children[value_input_idx]["type"] == "Input":
            value = children[value_input_idx]["props"]["value"]
        else:
            value = children[value_input_idx]["props"]["on"]
    return value


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


def confirm_button_click(
    n_clicks: Optional[int],
    sidebar_children: list[InputComponent],
    elements: GraphElements,
    dropdown_options: Optional[list],
    data: list
) -> tuple[GraphElements, Optional[list], list]:
    if (
        n_clicks is None
        or n_clicks < 1
        or len(sidebar_children) == 0
        or sidebar_children[0]["props"]["id"] == "confirm-edit-button"
    ):
        return elements, dropdown_options, data
    ATTRIBUTE_INPUT_FIELDS_START_IDX = get_attribute_input_field_start(sidebar_children)
    selected_items = Selected_items()
    selected_items.set_data(data)
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
    return elements, new_common_attrs, selected_items.get_data()


def add_button_click(
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
    dropdown_options: list,
    new_attribute_name: Optional[str],
    attr_val_container_children: Optional[list],
    type_dropdown_value: str,
    data: list
) -> tuple[GraphElements, list, list]:
    if (
        n_clicks is None
        or n_clicks < 1
        or new_attribute_name is None
        or new_attribute_name == ""
        or attr_val_container_children is None
        or len(attr_val_container_children) == 0
    ):
        return elements, sidebar_children, data
    REMOVE_DROPDOWN_OFFSET_FROM_CONFIRM = 1
    NEW_ATTRIBUTE_FIELD_NAME_OFFSET = 4
    ADD_ATTRIBUTE_BUTTON_OFFSET = 6
    new_attribute_value = extract_value_from_children(
        attr_val_container_children, dropdown_value=type_dropdown_value
    )
    selected_items = Selected_items()
    selected_items.set_data(data)
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
    return elements, sidebar_children, selected_items.get_data()


def remove_button_click(
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
    remove_options: list,
    remove_value: Optional[str],
    data: list
) -> tuple[GraphElements, list, list]:
    if n_clicks is None or n_clicks < 1 or remove_value is None or remove_value == "":
        return elements, sidebar_children, data
    selected_items = Selected_items()
    selected_items.set_data(data)
    elements_idxs = selected_items.get_elements_idxs()
    for element_idx in elements_idxs:
        elements[element_idx]["data"][ADD_ATTRS].pop(remove_value)
    common_attrs = selected_items.get_attrs()
    remove_options.remove(remove_value)
    FIRST_ATTR_INPUT_IDX = get_attribute_input_field_start(sidebar_children)
    CONFIRM_IDX = 0
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
    ATTRIBUTE_NAME_TO_BE_DELETED_IDX = 0
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
    return elements, sidebar_children, selected_items.get_data()


# APP CALLBACKS
@app.callback(
    [Output("sidebar_container", "children"),
     Output("selected-items", "data")],
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
) -> list:
    selected_nodes, selected_edges = optional_none_to_empty_list(
        selected_nodes
    ), optional_none_to_empty_list(selected_edges)
    selected_nodes_edges = selected_nodes + selected_edges
    if len(selected_nodes_edges) == 0:
        return [[], []]
    sidebar_children = []
    attributes: list = []
    additional_attrs = []
    for selected_item in selected_nodes_edges:
        additional_attr = selected_item[ADD_ATTRS]
        attributes.append(extract_attribute_names(additional_attr))
        additional_attrs.append(additional_attr)
    common_attr = list(reduce(set.intersection, attributes))  # type: ignore
    selected_items = Selected_items()
    selected_items.set_attrs(common_attr)
    selected_items.set_elements(selected_nodes_edges)
    selected_items.set_nodes(selected_nodes)
    selected_items.set_edges(selected_edges)
    selected_items.generate_selected_elements_idxs(elements)
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
    return [sidebar, selected_items.get_data()]


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


@app.callback(
    Output("remove-attribute-button", "disabled"),
    Input("remove-attribute-dropdown", "value"),
)
def remove_button_disabler(dropdown_value: Optional[str]) -> bool:
    return dropdown_value is None or dropdown_value == ""
