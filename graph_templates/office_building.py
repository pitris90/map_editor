import networkx # type: ignore
from typing import Optional


def office_building(
    floors: int,
    halls: int,
    office_att: Optional[dict] = None,
    hall_att: Optional[dict] = None,
) -> networkx.Graph:
    """Office Building Graph
    Args:
        Number of Floors - floors: Amount of Floors in Office Building
        Number of Halls - halls: Amount of Halls in Office Building
        Office Attribute - office_att: Attributes of Office nodes
        Hall Attribute - hall_att: Attributes of Hall nodes

    Returns:
        Graph: The generated networkx graph
    """
    office_attributes = dict(
        value=100, attack_len=112, blindness=0.0, memory=1, target=True
    )
    office_attributes.update(office_att or {})
    hall_attributes = dict(memory=4, target=False)
    hall_attributes.update(hall_att or {})
    graph = networkx.Graph()
    nodes = []
    edges = []
    for floor in range(floors):
        for hall in range(halls):
            up = f"Office_{floor}_{hall}up"
            dn = f"Office_{floor}_{hall}dn"
            cr = f"Hall_{floor}_{hall}"
            nodes += [
                (up, office_attributes),
                (dn, office_attributes),
                (cr, hall_attributes),
            ]
            edges += [(cr, up, dict(len=5)), (cr, dn, dict(len=5))]

        le = f"Office_{floor}_0le"
        ri = f"Office_{floor}_{halls - 1}ri"
        nodes += [(le, office_attributes), (ri, office_attributes)]
        edges += [
            (le, f"Hall_{floor}_0", dict(len=5)),
            (ri, f"Hall_{floor}_{halls - 1}", dict(len=5)),
        ]

        for hall in range(halls - 1):
            edges.append(
                (f"Hall_{floor}_{hall}", f"Hall_{floor}_{hall + 1}", dict(len=2))
            )

    for floor in range(floors - 1):
        edges += [
            (f"Hall_{floor}_0", f"Hall_{floor + 1}_0", dict(len=10)),
            (
                f"Hall_{floor}_{halls - 1}",
                f"Hall_{floor + 1}_{halls - 1}",
                dict(len=10),
            ),
        ]

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    graph.name = f"office_building_{floors}_f_{halls}_h"

    return graph
