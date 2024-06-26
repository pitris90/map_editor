from app import app
from dash_extensions.enrich import (  # type: ignore
    Output,
    Input,
    State,
    html,
    dcc,
    ALL,
    ctx
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
import copy
from functools import reduce
from css_stylesheets import (
    ATTRIBUTE_SIDEBAR_STYLE,
    BUTTON,
    BUTTON_IMG,
    STRING_ROW_COLOR,
    NUMBER_ROW_COLOR,
    DICT_ROW_COLOR,
    BOOL_ROW_COLOR,
    ROW,
    ROW_INPUT,
    ROW_INPUT_INPUT,
    ROW_VAL,
    ROW_ROW,
    BUTTONS
)

# Constants for indexing selected_items data
COMMON_ATTRS = 0
ELEMENTS = 1
EDGES = 2
NODES = 3
ELEMENTS_IDXS = 4

# Constants for general indexing
LABEL_TEXT_VALUE_IDX = 2

BOOL_SYMBOL = "1/0"
TEXT_SYMBOL = "A"
DICT_SYMBOL = "{}"
NUM_SYMBOL = "#"

# Template for label rows
LABEL_ROW_TEXT = html.Div(
    children=[
        html.Span(children=html.Img(
                    src="assets/text.svg",
                    alt=TEXT_SYMBOL,
                    style=BUTTON_IMG
                ),
                style=ROW_VAL),
        html.Span(children="Label", style=ROW_INPUT),
        html.Span(children="", id="label_text_value", style=ROW_INPUT | ROW_INPUT_INPUT),
        html.Div(
            children=html.Button(
                id="label_edit_pencil",
                children=html.Img(
                    src="assets/pencil.svg",
                    alt="Pencil image not found",
                    style=BUTTON_IMG
                ),
                style=BUTTON
            ), style=BUTTONS
        )
    ],
    style=ROW | STRING_ROW_COLOR | ROW_ROW
)
LABEL_ROW_EDIT = html.Div(
    children=[
        html.Span(children=html.Img(
                    src="assets/text.svg",
                    alt=TEXT_SYMBOL,
                    style=BUTTON_IMG
                ),
                style=ROW_VAL),
        html.Span(children="Label", style=ROW_INPUT),
        dbc.Input(value="",
                  id="label_edit_value",
                  type="text", placeholder="Label",
                  style=ROW_INPUT | ROW_INPUT_INPUT),
        html.Span(children=[
            html.Button(
                id="label_edit_cancel",
                children=html.Img(
                    src="assets/close.svg",
                    alt="Cross image not found",
                    style=BUTTON_IMG
                ),
                style=BUTTON
            ),
            html.Button(
                id="label_edit_confirm",
                children=html.Img(
                    src="assets/check.svg",
                    alt="Tick image not found",
                    style=BUTTON_IMG
                ),
                style=BUTTON
            )],
            style=BUTTONS
        )
    ],
    style=ROW | STRING_ROW_COLOR | ROW_ROW
)

NAME_TYPE_TEMPLATE = dbc.Input(
    id={
        "type": "attr_name_input"
    },
    type="text",
    style=ROW_INPUT | ROW_INPUT_INPUT
)


VALUE_TYPE_TEMPLATES = {
    "bool": [BOOL_SYMBOL, html.Img(
                    src="assets/bool.svg",
                    alt=BOOL_SYMBOL,
                    style=BUTTON_IMG
                )],
    "text": [TEXT_SYMBOL, html.Img(
                    src="assets/text.svg",
                    alt=TEXT_SYMBOL,
                    style=BUTTON_IMG
                )],
    "dict": [DICT_SYMBOL, html.Img(
                    src="assets/dict.svg",
                    alt=DICT_SYMBOL,
                    style=BUTTON_IMG
                )],
    "number": [NUM_SYMBOL, html.Img(
                    src="assets/numeric.svg",
                    alt=NUM_SYMBOL,
                    style=BUTTON_IMG
                )],
    BOOL_SYMBOL: daq.BooleanSwitch(  # type: ignore
            id={
                "type": "attr_value_input",
            },
            style=ROW_INPUT | ROW_INPUT_INPUT
    ),
    TEXT_SYMBOL: dbc.Input(
        id={
            "type": "attr_value_input"
        },
        type="text",
        style=ROW_INPUT | ROW_INPUT_INPUT
    ),
    DICT_SYMBOL: dbc.Input(
        id={
            "type": "attr_value_input"
        },
        type="text",
        style=ROW_INPUT | ROW_INPUT_INPUT
    ),
    NUM_SYMBOL: dbc.Input(
        id={
            "type": "attr_value_input"
        },
        type="number",
        style=ROW_INPUT | ROW_INPUT_INPUT
    )
}

ATTR_ROW_COLORS = {
    TEXT_SYMBOL: STRING_ROW_COLOR,
    NUM_SYMBOL: NUMBER_ROW_COLOR,
    DICT_SYMBOL: DICT_ROW_COLOR,
    BOOL_SYMBOL: BOOL_ROW_COLOR
}

TEXT_BUTTONS_TEMPLATE = html.Div(
        children=[html.Button(
            id={
                "type": "attr_edit_pencil"
            },
            children=html.Img(
                src="assets/pencil.svg",
                alt="Pencil image not found",
                style=BUTTON_IMG
            ),
            style=BUTTON
        ), html.Button(
            id={
                "type": "attr_delete"
            },
            children=html.Img(
                src="assets/delete.svg",
                alt="Dust Bin image not found",
                style=BUTTON_IMG
            ),
            style=BUTTON
        )],
        style=BUTTONS
)

EDIT_BUTTONS_TEMPLATE = html.Div(
        children=[
            html.Button(
                id={
                    "type": "attr_edit_cancel"
                },
                children=html.Img(
                    src="assets/close.svg",
                    alt="Cross image not found",
                    style=BUTTON_IMG
                ),
                style=BUTTON
            ),
            html.Button(
                id={
                    "type": "attr_edit_confirm"
                },
                children=html.Img(
                    src="assets/check.svg",
                    alt="Tick image not found",
                    style=BUTTON_IMG
                ),
                style=BUTTON
            )],
        style=BUTTONS
)


ROW_SYMBOL_IDX = 0
ROW_TYPE_IMG_IDX = 1
TYPE_SYMBOL_IDX = 0
ATTR_NAME_IDX = 1
ATTR_VALUE_IDX = 2
LABEL_ROW_SIDEBAR_IDX = 0

ID_AFTER_ATTRIBUTE_ROWS = "attribute-type-dropdown"
FIRST_ROW_BUTTON_IDX = 3
PROPS = "props"
CHILDREN = "children"
TYPE = "type"
ID = "id"
INDEX = "index"
NAME_ELEMENT = "name-ele"
VALUE_ELEMENT = "value-ele"
VALUE = "value"
ON = "on"
ATTR_VALUE_COUNT_TYPE = "attr_value_count"
DATA = "data"
DIS = "disabled"
LABEL = "label"
ALT = "alt"


class ConstError(ValueError):
    """Raised when the value of the constant is not expected"""

    pass


class IdxError(ValueError):
    """Raised when the value of the index is not expected"""

    pass


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


def is_real_click(
    triggered,
    trigger_n_clicks
):
    if triggered is None \
       or trigger_n_clicks is None:
        return False
    triggered_id = str(triggered["index"])
    for row in trigger_n_clicks:
        if triggered_id in row["prop_id"] and (row["value"] is None or row["value"] == 0):
            return False
    return True


def get_row_list_idx(
    id: int,  # index of attribute row in id["index"]
    row_id_list: list  # list of all row element's ids of some element in attr row
) -> Optional[int]:
    for i in range(len(row_id_list)):
        if row_id_list[i]["index"] == id:
            return i
    return None


def get_sidebar_div_children_row_idx(
    id: int,  # index of attribute row in id["index"]
    sidebar_div_children: list
) -> Optional[int]:
    wanted_id = "attr_row_index" + str(id)
    for i in range(len(sidebar_div_children)):
        element_id = sidebar_div_children[i][PROPS].get(ID)
        if element_id is not None and element_id == wanted_id:
            return i
    return None


def get_insert_row_idx(sidebar_children: list) -> tuple[int, int]:
    last_id = None
    add_dropdown = None
    for i in range(len(sidebar_children)):
        id = sidebar_children[i][PROPS].get("id")
        if id is not None:
            if "attr_row_index" in id:
                last_id = int(id[len("attr_row_index"):])
            elif id == "attribute-type-dropdown":
                add_dropdown = i
                break
    if add_dropdown is None:
        raise IdxError()
    if last_id is None:
        last_id = add_dropdown - 1
    else:
        last_id += 1
    return add_dropdown, last_id


def add_buttons_index(buttons: html.Div, row_idx: int) -> None:
    buttons.children[0].id[INDEX] = row_idx  # type: ignore
    buttons.children[1].id[INDEX] = row_idx  # type: ignore


def determine_value_type(input_value: InputValue) -> str:
    if isinstance(input_value, bool):
        return "bool"
    if isinstance(input_value, str):
        return "text"
    if (
        isinstance(input_value, dict)
        or isinstance(input_value, list)
        or isinstance(input_value, set)
    ):
        return "dict"
    return "number"


def create_attribute_text_row(
    attr_name: str,
    attr_value: InputValue,
    value_count: int,
    index: int
) -> html.Div:
    attr_row_items = []
    value_type = determine_value_type(attr_value)
    type_symbol = VALUE_TYPE_TEMPLATES[value_type][ROW_SYMBOL_IDX]
    type_img = VALUE_TYPE_TEMPLATES[value_type][ROW_TYPE_IMG_IDX]
    attr_row_items.append(html.Span(
        children=type_img,
        id={
            "type": "attr_type_symbol",
            "index": index
        },
        style=ROW_VAL
    ))
    attr_row_items.append(html.Span(
        children=attr_name,
        id={
            "type": "attr_name_text",
            "index": index
        },
        style=ROW_INPUT
    ))
    if value_count == 1:
        attr_row_items.append(html.Span(
            children=str(attr_value),
            id={
                "type": "attr_value_text",
                "index": index
            },
            style=ROW_INPUT | ROW_INPUT_INPUT
        ))
    else:
        attr_row_items.append(html.Span(
            children="#: " + str(value_count),
            id={
                "type": ATTR_VALUE_COUNT_TYPE,
                "index": index
            },
            style=ROW_INPUT | ROW_INPUT_INPUT
        ))

    text_buttons = copy.deepcopy(TEXT_BUTTONS_TEMPLATE)
    add_buttons_index(text_buttons, index)
    attr_row_items.append(text_buttons)
    return html.Div(
        children=attr_row_items,
        id="attr_row_index" + str(index),
        style=ROW | ATTR_ROW_COLORS[type_symbol] | ROW_ROW
    )


def create_label_row(label: str, row_template: html.Div) -> html.Div:
    if row_template.children is None:
        raise ConstError()
    row_template.children[LABEL_TEXT_VALUE_IDX].children = label
    return row_template


def update_elements_attributes_name(
    element_idxs: list,
    elements: GraphElements,
    new_name: str,
    old_name: str,
    common_attrs: list
) -> None:
    for element_idx in element_idxs:
        elements[element_idx][DATA][ADD_ATTRS][new_name] = \
            elements[element_idx][DATA][ADD_ATTRS].pop(old_name)
    common_attrs[common_attrs.index(old_name)] = new_name


def update_elements_attributes_value(
    element_idxs: list,
    elements: GraphElements,
    new_value: InputValue,
    name: str
) -> None:
    for element_idx in element_idxs:
        elements[element_idx][DATA][ADD_ATTRS][name] = new_value


def update_attribute_rows_indices(
    sidebar_children: list,
    row_idx: int,
    increment: int,
    previous_attr_values: dict
) -> None:
    while sidebar_children[row_idx][PROPS][ID] != ID_AFTER_ATTRIBUTE_ROWS:
        new_idx = row_idx + increment
        if previous_attr_values.get(row_idx) is not None:
            previous_attr_values[new_idx] = previous_attr_values.pop(row_idx)
        sidebar_children[row_idx][PROPS][ID] = "attr_row_index" + str(new_idx)
        row_children = sidebar_children[row_idx][PROPS][CHILDREN]
        update_attribute_row_indices(row_children, new_idx)
        row_idx += 1


def update_attribute_row_indices(row_children: list, new_idx: int) -> None:
    FIRST_BUTTON_IDX = 0
    SECOND_BUTTON_IDX = 1
    for i in range(len(row_children)):
        if i >= FIRST_ROW_BUTTON_IDX:
            row_children[i][PROPS][CHILDREN][FIRST_BUTTON_IDX][PROPS][ID][INDEX] = new_idx
            row_children[i][PROPS][CHILDREN][SECOND_BUTTON_IDX][PROPS][ID][INDEX] = new_idx
            continue
        row_children[i][PROPS][ID][INDEX] = new_idx


def update_attr_row(
    selected_items: Selected_items,
    elements: GraphElements,
    sidebar_child: dict
) -> None:
    if sidebar_child[PROPS][CHILDREN][ATTR_NAME_IDX][TYPE] == "Input":
        return


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
    n_clicks: list,
    sidebar_children: list[InputComponent],
    elements: GraphElements,
    row_button_ids: list,
    row_names: list,
    data: list,
    previous_attr_elements: dict
) -> tuple[GraphElements, Optional[list], list, dict]:
    triggered = ctx.triggered_id
    triggered_n_clicks = ctx.triggered
    if not is_real_click(triggered, triggered_n_clicks):
        return elements, sidebar_children, data, previous_attr_elements
    row_idx = triggered["index"]  # type: ignore
    row_sidebar_idx = get_sidebar_div_children_row_idx(row_idx, sidebar_children)
    if row_sidebar_idx is None:
        raise IdxError()
    str_row_idx = str(row_idx)
    row_children = sidebar_children[row_sidebar_idx][PROPS][CHILDREN]
    selected_items = Selected_items()
    selected_items.set_data(data)
    element_idxs = selected_items.get_elements_idxs()
    common_attrs = selected_items.get_attrs()
    first_element_idx = element_idxs[0]
    value_count = 1

    old_name = previous_attr_elements[str_row_idx][NAME_ELEMENT][PROPS][CHILDREN]
    new_name = row_children[ATTR_NAME_IDX][PROPS][VALUE]
    attr_value_props = row_children[ATTR_VALUE_IDX][PROPS]
    new_value = elements[first_element_idx][DATA][ADD_ATTRS][old_name]
    type_symbol = row_children[TYPE_SYMBOL_IDX][PROPS][CHILDREN][PROPS][ALT]
    update_elements_attributes_name(element_idxs, elements, new_name, old_name, common_attrs)
    if attr_value_props[ID][TYPE] == ATTR_VALUE_COUNT_TYPE:
        value_count = int(attr_value_props[CHILDREN][3:])
    else:
        if type_symbol == BOOL_SYMBOL:
            new_value = attr_value_props[ON]
        elif type_symbol == DICT_SYMBOL:
            new_value = ast.literal_eval(attr_value_props[VALUE])
        elif type_symbol == NUM_SYMBOL:
            new_value = int(attr_value_props[VALUE])
        else:
            new_value = attr_value_props[VALUE]
        update_elements_attributes_value(element_idxs, elements, new_value, new_name)

    new_text_row = create_attribute_text_row(new_name, new_value, value_count, row_idx)
    sidebar_children[row_sidebar_idx] = new_text_row

    del previous_attr_elements[str_row_idx]
    selected_items.set_attrs(common_attrs)
    return elements, sidebar_children, selected_items.get_data(), previous_attr_elements


def add_button_click(
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
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
    NEW_ATTRIBUTE_FIELD_NAME_OFFSET = 1
    ADD_ATTRIBUTE_BUTTON_OFFSET = 3
    new_attribute_value = extract_value_from_children(
        attr_val_container_children, dropdown_value=type_dropdown_value
    )
    selected_items = Selected_items()
    selected_items.set_data(data)
    common_attrs = selected_items.get_attrs()
    common_attrs.append(new_attribute_name)
    selected_items.set_attrs(common_attrs)
    elements_idxs = selected_items.get_elements_idxs()
    for element_idx in elements_idxs:
        elements[element_idx][DATA][ADD_ATTRS][new_attribute_name] = new_attribute_value

    insert_idx, new_row_idx = get_insert_row_idx(sidebar_children)

    sidebar_children[insert_idx + NEW_ATTRIBUTE_FIELD_NAME_OFFSET][PROPS][VALUE] = ""
    sidebar_children[insert_idx + ADD_ATTRIBUTE_BUTTON_OFFSET][PROPS][DIS] = True
    sidebar_children.insert(
        insert_idx,
        create_attribute_text_row(new_attribute_name, new_attribute_value, 1, new_row_idx),
    )
    return elements, sidebar_children, selected_items.get_data()


def remove_button_click(
    n_clicks: list,
    sidebar_children: list,
    elements: GraphElements,
    row_button_ids: list,
    row_values: list,
    data: list,
    previous_attr_values: dict
) -> tuple[GraphElements, list, list, dict]:
    triggered = ctx.triggered_id
    trigger_n_clicks = ctx.triggered
    if not is_real_click(triggered, trigger_n_clicks):
        return elements, sidebar_children, data, previous_attr_values

    row_idx = triggered["index"]  # type: ignore
    selected_items = Selected_items()
    selected_items.set_data(data)
    elements_idxs = selected_items.get_elements_idxs()
    row_list_idx = get_row_list_idx(row_idx, row_button_ids)
    if row_list_idx is None:
        raise IdxError()
    remove_value = row_values[row_list_idx]
    for element_idx in elements_idxs:
        elements[element_idx]["data"][ADD_ATTRS].pop(remove_value)
    common_attrs = selected_items.get_attrs()
    common_attrs.remove(remove_value)
    selected_items.set_attrs(common_attrs)

    update_attribute_rows_indices(sidebar_children, row_idx + 1, -1, previous_attr_values)
    sidebar_children.pop(row_idx)
    return elements, sidebar_children, selected_items.get_data(), previous_attr_values


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
def create_attribute_editor_sidebar(
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
        sidebar_children.append(create_label_row(selected_nodes[0]["label"], LABEL_ROW_TEXT))
    sidebar_children.append(
        html.H5("Attributes", id="elements_prop_fields_heading")
    )
    index = len(sidebar_children)
    for attr in common_attr:
        number_of_values = count_unique_values(additional_attrs, attr)
        sidebar_children.append(create_attribute_text_row(
            attr, additional_attrs[0][attr], number_of_values, index
        ))
        index += 1
    sidebar_children.append(
        dcc.Dropdown(
            ["Number", "Boolean", "Text", "Dictionary"],
            placeholder="Select Attribute Value Type",
            id=ID_AFTER_ATTRIBUTE_ROWS,
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
        Output("sidebar_div", "children"),
        Output("previous-attr-elements", "data")
    ],
    [
        Input({"type": "attr_edit_pencil", "index": ALL}, "n_clicks"),
        State("sidebar_div", "children"),
        State("previous-attr-elements", "data"),
        State("selected-items", "data"),
        State("graph-cytoscape", "elements")
    ],
    prevent_initial_call=True
)
def create_attribute_input_row(
    n_clicks: list,
    sidebar_children: list,
    prev_attr_elements: dict,
    data: list,
    elements: GraphElements
) -> tuple[list, dict]:
    triggered = ctx.triggered_id
    triggered_n_clicks = ctx.triggered
    input_row_items = []
    if not is_real_click(triggered, triggered_n_clicks):
        return sidebar_children, prev_attr_elements
    row_idx = triggered["index"]  # type: ignore
    selected_items = Selected_items()
    selected_items.set_data(data)
    element_idxs = selected_items.get_elements_idxs()
    old_row_items = sidebar_children[row_idx][PROPS][CHILDREN]
    input_row_items.append(old_row_items[TYPE_SYMBOL_IDX])

    name_input = copy.deepcopy(NAME_TYPE_TEMPLATE)
    name_input.id["index"] = row_idx  # type: ignore
    name_element = old_row_items[ATTR_NAME_IDX]
    name = name_element[PROPS][CHILDREN]
    name_input.value = name  # type: ignore
    input_row_items.append(name_input)

    attr_value_text_element = old_row_items[ATTR_VALUE_IDX]
    type_symbol = old_row_items[TYPE_SYMBOL_IDX][PROPS][CHILDREN][PROPS][ALT]
    if attr_value_text_element[PROPS][ID][TYPE] == ATTR_VALUE_COUNT_TYPE:
        input_row_items.append(attr_value_text_element)
    else:
        attr_value_input = copy.deepcopy(VALUE_TYPE_TEMPLATES[type_symbol])
        attr_value_input.id["index"] = row_idx
        attr_value = old_row_items[ATTR_VALUE_IDX][PROPS][CHILDREN]
        if type_symbol == BOOL_SYMBOL:
            attr_value = ast.literal_eval(attr_value)
            attr_value_input.on = attr_value
        else:
            attr_value_input.value = attr_value
        input_row_items.append(attr_value_input)

    edit_buttons = copy.deepcopy(EDIT_BUTTONS_TEMPLATE)
    add_buttons_index(edit_buttons, row_idx)
    input_row_items.append(edit_buttons)

    attr_input_row = html.Div(
        children=input_row_items,
        id="attr_row_index" + str(row_idx),
        style=ROW | ATTR_ROW_COLORS[type_symbol] | ROW_ROW
    )
    sidebar_children[row_idx] = attr_input_row
    prev_attr_elements[str(row_idx)] = {NAME_ELEMENT: name_element,
                                        VALUE_ELEMENT: attr_value_text_element,
                                        VALUE: elements[element_idxs[0]][DATA][ADD_ATTRS][name]}
    return sidebar_children, prev_attr_elements


@app.callback(
    [
        Output("sidebar_div", "children"),
        Output("previous-attr-elements", "data")
    ],
    [
        Input({"type": "attr_edit_cancel", "index": ALL}, "n_clicks"),
        State("sidebar_div", "children"),
        State("previous-attr-elements", "data")
    ],
    prevent_initial_call=True
)
def cancel_attr_edit(
    n_clicks: Optional[int],
    sidebar_children: list,
    previous_attr_elements: dict
) -> tuple[list, dict]:
    triggered = ctx.triggered_id
    triggered_n_clicks = ctx.triggered
    if not is_real_click(triggered, triggered_n_clicks):
        return sidebar_children, previous_attr_elements
    row_idx = triggered["index"]  # type: ignore
    str_row_idx = str(row_idx)
    text_row_items = []
    old_row_items = sidebar_children[row_idx][PROPS][CHILDREN]
    text_row_items.append(old_row_items[TYPE_SYMBOL_IDX])
    type_symbol = old_row_items[TYPE_SYMBOL_IDX][PROPS][CHILDREN][PROPS][ALT]

    text_row_items.append(previous_attr_elements[str_row_idx][NAME_ELEMENT])

    text_row_items.append(previous_attr_elements[str_row_idx][VALUE_ELEMENT])

    text_buttons = copy.deepcopy(TEXT_BUTTONS_TEMPLATE)
    add_buttons_index(text_buttons, row_idx)
    text_row_items.append(text_buttons)

    attr_text_row = html.Div(
        children=text_row_items,
        id="attr_row_index" + str(row_idx),
        style=ROW | ATTR_ROW_COLORS[type_symbol] | ROW_ROW
    )
    sidebar_children[row_idx] = attr_text_row
    del previous_attr_elements[str_row_idx]
    return sidebar_children, previous_attr_elements


@app.callback(
    [
        Output("sidebar_div", "children")
    ],
    [
        Input("graph-cytoscape", "elements"),
        State("sidebar_div", "children"),
        State("selected-items", "data")
    ],
)
def update_attribute_editor_sidebar(
    elements: GraphElements,
    sidebar_children: list[dict],
    data: list
) -> list:
    if len(sidebar_children) == 0:
        return []
    selected_items = Selected_items()
    selected_items.set_data(data)
    for sidebar_child in sidebar_children:
        child_id = sidebar_child["props"].get("id")
        if child_id is not None and "attr_row_index" in child_id:
            update_attr_row(selected_items, elements, sidebar_child)
    return sidebar_children


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
        input_field = daq.BooleanSwitch(  # type: ignore
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
    [
        Output("sidebar_div", "children"),
        Output("previous-attr-elements", "data")
    ],
    [
        Input("label_edit_pencil", "n_clicks"),
        State("sidebar_div", "children"),
        State("previous-attr-elements", "data"),
        State("label_text_value", "children")
    ],
    prevent_initial_call=True
)
def create_label_input_row(
    n_clicks: Optional[int],
    sidebar_children: list,
    prev_attr_elements: dict,
    label: str
) -> tuple[list, dict]:
    if n_clicks is None \
       or n_clicks < 1:
        return sidebar_children, prev_attr_elements

    label_input_row = copy.deepcopy(LABEL_ROW_EDIT)
    label_input_row.children[ATTR_VALUE_IDX].value = label  # type: ignore
    sidebar_children[LABEL_ROW_SIDEBAR_IDX] = label_input_row
    prev_attr_elements[LABEL] = label
    return sidebar_children, prev_attr_elements


@app.callback(
    [
        Output("sidebar_div", "children"),
        Output("previous-attr-elements", "data")
    ],
    [
        Input("label_edit_cancel", "n_clicks"),
        State("sidebar_div", "children"),
        State("previous-attr-elements", "data")
    ],
    prevent_initial_call=True
)
def cancel_label_edit(
    n_clicks: Optional[int],
    sidebar_children: list,
    prev_attr_elements: dict
) -> tuple[list, dict]:
    if n_clicks is None \
       or n_clicks < 1:
        return sidebar_children, prev_attr_elements
    old_label = prev_attr_elements[LABEL]

    label_text_row = create_label_row(old_label, LABEL_ROW_TEXT)

    sidebar_children[LABEL_ROW_SIDEBAR_IDX] = label_text_row
    del prev_attr_elements[LABEL]
    return sidebar_children, prev_attr_elements


def confirm_label_button_click(
    n_clicks: Optional[int],
    sidebar_children: list[InputComponent],
    elements: GraphElements,
    data: list,
    previous_attr_elements: dict,
    new_label: str
) -> tuple[GraphElements, Optional[list], dict]:
    if n_clicks is None \
       or n_clicks < 1:
        return elements, sidebar_children, previous_attr_elements

    selected_items = Selected_items()
    selected_items.set_data(data)
    element_idxs = selected_items.get_elements_idxs()
    first_element_idx = element_idxs[0]

    elements[first_element_idx][DATA][LABEL] = new_label

    new_text_row = create_label_row(new_label, LABEL_ROW_TEXT)

    sidebar_children[LABEL_ROW_SIDEBAR_IDX] = new_text_row

    del previous_attr_elements[LABEL]
    return elements, sidebar_children, previous_attr_elements
