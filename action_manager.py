from app import app
from dash_extensions.enrich import (  # type: ignore
    Output,
    Input,
    State
)
from typing import Optional
from type_aliases import (
    GraphElements,
    GraphElement,
    InputComponent,
    U_R_Actions_Init
)
from canvas import (
    add_node,
    delete_node,
    delete_edge,
    update_positions,
    rebind_new_edge
)
from attribute_editor import (
    confirm_button_click,
    add_button_click,
    remove_button_click
)


CURRENT_ACTION_ID = 0
UNDO_ACTION_ID = 0
REDO_ACTION_ID = 1


def insert_u_r_action(
    u_r_actions: U_R_Actions_Init,
    before_action: GraphElements,
    current_state: GraphElements
) -> U_R_Actions_Init:
    if before_action == current_state:
        return u_r_actions
    current_action_id = u_r_actions[CURRENT_ACTION_ID]
    if current_action_id + 1 != len(u_r_actions):
        u_r_actions = u_r_actions[:current_action_id + 1]
    if current_action_id == 0 or u_r_actions[current_action_id] != before_action:
        u_r_actions.append(before_action)
        u_r_actions[CURRENT_ACTION_ID] += 1
    u_r_actions.append(current_state)
    u_r_actions[CURRENT_ACTION_ID] += 1
    return u_r_actions


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("graph-cytoscape", "dblTapData"),
        State("graph-cytoscape", "elements"),
        State("undo-redo-actions", "data")
    ],
)
def action_add_node(
    pos: Optional[dict],
    elements: GraphElements,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, U_R_Actions_Init]:
    before_action = list(elements)
    add_node_output = add_node(pos, elements)
    return add_node_output, insert_u_r_action(u_r_actions, before_action, add_node_output)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("graph-cytoscape", "dblTapNode"),
        State("graph-cytoscape", "elements"),
        State("undo-redo-actions", "data")
    ],
)
def action_delete_node(
    node: Optional[GraphElement],
    elements: GraphElements,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, U_R_Actions_Init]:
    before_action = list(elements)
    delete_node_output = delete_node(node, elements)
    return delete_node_output, insert_u_r_action(u_r_actions, before_action, delete_node_output)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("graph-cytoscape", "dblTapEdge"),
        State("graph-cytoscape", "elements"),
        State("undo-redo-actions", "data")
    ],
)
def action_delete_edge(
    edge: Optional[GraphElement],
    elements: GraphElements,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, U_R_Actions_Init]:
    before_action = list(elements)
    delete_edge_output = delete_edge(edge, elements)
    return delete_edge_output, insert_u_r_action(u_r_actions, before_action, delete_edge_output)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("graph-cytoscape", "ele_move_pos"),
        State("graph-cytoscape", "ele_move_data"),
        State("graph-cytoscape", "elements"),
        State("graph-cytoscape", "selectedNodeData"),
        State("selected-items", "data"),
        State("undo-redo-actions", "data")
    ],
)
def action_update_positions(
    new_node_position: dict,
    moved_node_data: dict,
    elements: GraphElements,
    selected_node_data: Optional[list],
    data: list,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, U_R_Actions_Init]:
    before_action = list(elements)
    positions_output = update_positions(
        new_node_position,
        moved_node_data,
        elements,
        selected_node_data,
        data)
    return positions_output, insert_u_r_action(u_r_actions, before_action, positions_output)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("graph-cytoscape", "ehcompleteSource"),
        Input("graph-cytoscape", "ehcompleteTarget"),
        State("graph-cytoscape", "elements"),
        State("orientation-graph-switcher", "on"),
        State("undo-redo-actions", "data")
    ],
)
def action_rebind_new_edge(
    source: Optional[GraphElement],
    target: Optional[GraphElement],
    elements: GraphElements,
    directed: bool,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, U_R_Actions_Init]:
    before_action = list(elements)
    rebind_new_edge_output = rebind_new_edge(source, target, elements, directed)
    return rebind_new_edge_output, insert_u_r_action(u_r_actions, before_action,
                                                     rebind_new_edge_output)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("remove-attribute-dropdown", "options"),
        Output("selected-items", "data"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("confirm-edit-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("selected-items", "data"),
        State("undo-redo-actions", "data")
    ],
    prevent_initial_call=True,
)
def action_confirm_button_click(
    n_clicks: Optional[int],
    sidebar_children: list[InputComponent],
    elements: GraphElements,
    dropdown_options: Optional[list],
    data: list,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, Optional[list], list, U_R_Actions_Init]:
    before_action = list(elements)
    confirm_button_click_output = confirm_button_click(
        n_clicks,
        sidebar_children,
        elements,
        dropdown_options,
        data)
    return confirm_button_click_output + (insert_u_r_action(u_r_actions, before_action,
                                                            confirm_button_click_output[0]),)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("sidebar_div", "children"),
        Output("selected-items", "data"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("add-attribute-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("add-attribute-name", "value"),
        State("add-attribute-value-container", "children"),
        State("attribute-type-dropdown", "value"),
        State("selected-items", "data"),
        State("undo-redo-actions", "data")
    ],
    prevent_initial_call=True,
)
def action_add_button_click(
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
    dropdown_options: list,
    new_attribute_name: Optional[str],
    attr_val_container_children: Optional[list],
    type_dropdown_value: str,
    data: list,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, list, list, U_R_Actions_Init]:
    before_action = list(elements)
    add_button_click_output = add_button_click(
        n_clicks,
        sidebar_children,
        elements,
        dropdown_options,
        new_attribute_name,
        attr_val_container_children,
        type_dropdown_value,
        data
    )
    return add_button_click_output + (insert_u_r_action(u_r_actions, before_action,
                                                        add_button_click_output[0]),)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("sidebar_div", "children"),
        Output("selected-items", "data"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("remove-attribute-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("remove-attribute-dropdown", "value"),
        State("selected-items", "data"),
        State("undo-redo-actions", "data")
    ],
    prevent_initial_call=True,
)
def action_remove_button_click(
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
    remove_options: list,
    remove_value: Optional[str],
    data: list,
    u_r_actions: U_R_Actions_Init
) -> tuple[GraphElements, list, list, U_R_Actions_Init]:
    before_action = list(elements)
    remove_button_click_output = remove_button_click(
        n_clicks,
        sidebar_children,
        elements,
        remove_options,
        remove_value,
        data
    )
    return remove_button_click_output + (insert_u_r_action(u_r_actions, before_action,
                                                           remove_button_click_output[0]),)


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("graph-cytoscape", "undoClick"),
        State("graph-cytoscape", "elements"),
        State("undo-redo-actions", "data")
    ]
)
def undo(undo_click, elements, u_r_actions) -> tuple[GraphElements, U_R_Actions_Init]:
    if u_r_actions[CURRENT_ACTION_ID] <= 1 or undo_click == 0:
        return elements, u_r_actions
    u_r_actions[CURRENT_ACTION_ID] -= 1
    return u_r_actions[u_r_actions[CURRENT_ACTION_ID]], u_r_actions


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("undo-redo-actions", "data")
    ],
    [
        Input("graph-cytoscape", "redoClick"),
        State("graph-cytoscape", "elements"),
        State("undo-redo-actions", "data")
    ]
)
def redo(redo_click, elements, u_r_actions) -> tuple[GraphElements, U_R_Actions_Init]:
    if u_r_actions[CURRENT_ACTION_ID] == len(u_r_actions) - 1 or redo_click == 0:
        return elements, u_r_actions
    u_r_actions[CURRENT_ACTION_ID] += 1
    return u_r_actions[u_r_actions[CURRENT_ACTION_ID]], u_r_actions
