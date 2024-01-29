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
    InputComponent
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


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "dblTapData"),
        State("graph-cytoscape", "elements"),
    ],
)
def action_add_node(pos: Optional[dict], elements: GraphElements) -> GraphElements:
    add_node_output = add_node(pos, elements)
    return add_node_output


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "dblTapNode"),
        State("graph-cytoscape", "elements"),
    ],
)
def action_delete_node(
    node: Optional[GraphElement],
    elements: GraphElements
) -> GraphElements:
    delete_node_output = delete_node(node, elements)
    return delete_node_output


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "dblTapEdge"),
        State("graph-cytoscape", "elements"),
    ],
)
def action_delete_edge(
    edge: Optional[GraphElement],
    elements: GraphElements
) -> GraphElements:
    delete_edge_output = delete_edge(edge, elements)
    return delete_edge_output


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "ele_move_pos"),
        State("graph-cytoscape", "ele_move_data"),
        State("graph-cytoscape", "elements"),
        State("graph-cytoscape", "selectedNodeData"),
        State("selected-items", "data")
    ],
)
def action_update_positions(
    new_node_position: dict,
    moved_node_data: dict,
    elements: GraphElements,
    selected_node_data: Optional[list],
    data: list
) -> GraphElements:
    positions_output = update_positions(
        new_node_position,
        moved_node_data,
        elements,
        selected_node_data,
        data)
    return positions_output


@app.callback(
    Output("graph-cytoscape", "elements"),
    [
        Input("graph-cytoscape", "ehcompleteSource"),
        Input("graph-cytoscape", "ehcompleteTarget"),
        State("graph-cytoscape", "elements"),
        State("orientation-graph-switcher", "on"),
    ],
)
def action_rebind_new_edge(
    source: Optional[GraphElement],
    target: Optional[GraphElement],
    elements: GraphElements,
    directed: bool,
) -> GraphElements:
    rebind_new_edge_output = rebind_new_edge(source, target, elements, directed)
    return rebind_new_edge_output


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("remove-attribute-dropdown", "options"),
        Output("selected-items", "data")
    ],
    [
        Input("confirm-edit-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("selected-items", "data")
    ],
    prevent_initial_call=True,
)
def action_confirm_button_click(
    n_clicks: Optional[int],
    sidebar_children: list[InputComponent],
    elements: GraphElements,
    dropdown_options: Optional[list],
    data: list
) -> tuple[GraphElements, Optional[list], list]:
    confirm_button_click_output = confirm_button_click(
        n_clicks,
        sidebar_children,
        elements,
        dropdown_options,
        data)
    return confirm_button_click_output


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("sidebar_div", "children"),
        Output("selected-items", "data")
    ],
    [
        Input("add-attribute-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("add-attribute-name", "value"),
        State("add-attribute-value-container", "children"),
        State("attribute-type-dropdown", "value"),
        State("selected-items", "data")
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
    data: list
) -> tuple[GraphElements, list, list]:
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
    return add_button_click_output


@app.callback(
    [
        Output("graph-cytoscape", "elements"),
        Output("sidebar_div", "children"),
        Output("selected-items", "data")
    ],
    [
        Input("remove-attribute-button", "n_clicks"),
        State("sidebar_div", "children"),
        State("graph-cytoscape", "elements"),
        State("remove-attribute-dropdown", "options"),
        State("remove-attribute-dropdown", "value"),
        State("selected-items", "data")
    ],
    prevent_initial_call=True,
)
def action_remove_button_click(
    n_clicks: Optional[int],
    sidebar_children: list,
    elements: GraphElements,
    remove_options: list,
    remove_value: Optional[str],
    data: list
) -> tuple[GraphElements, list, list]:
    remove_button_click_output = remove_button_click(
        n_clicks,
        sidebar_children,
        elements,
        remove_options,
        remove_value,
        data
    )
    return remove_button_click_output
