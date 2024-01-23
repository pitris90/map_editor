from typing import Optional
from type_aliases import (
    GraphElements,
    GraphElement,
)
from graph_utils import (
    is_node,
    ADD_ATTRS,
    id_generator,
    is_removable_edge
)
from attribute_editor import Selected_items


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


def update_positions(
    new_node_position: dict,
    moved_node_data: dict,
    elements: GraphElements,
    selected_node_data: Optional[list],
    data: list
) -> GraphElements:
    selected_items = Selected_items()
    selected_items.set_data(data)
    element_edited = False
    x_diff, y_diff = 0, 0
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
