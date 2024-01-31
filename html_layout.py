import dash_daq as daq
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from css_stylesheets import (INPUT_STYLESHEET,
                             CONTROLS_SIDEBAR_STYLE,
                             ROOT_DIV_STYLE)
from dash_extensions.enrich import (
    html,
    dcc
)
from graph_functions import dropdown_functions, FUNCTION_DICT


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


ATTRIBUTE_SIDEBAR_CONTAINER = html.Div(
    children=[],
    id="sidebar_container",
)


APP_LAYOUT = html.Div(
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
                dbc.Button("Generate Graph from Function", id="open", class_name="mb-2"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Graph Functions"),
                        dbc.ModalBody(children=GRAPH_TEMPLATES),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Generate Graph from Function",
                                id="graph_generate_button",
                                className="ml-auto",
                            )
                        ),
                    ],
                    id="modal_menu_graph_functions",
                ),
                daq.BooleanSwitch(  # type: ignore
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
            layout={"name": "preset"},
            autoRefreshLayout=True,
            boxSelectionEnabled=True,
        ),
        # html.Button("Debug Button", id="main-debug-button"),
        # html.Div(id="output-data-upload"),
        # html.Div(id="position_click"),
        ATTRIBUTE_SIDEBAR_CONTAINER,
        dcc.Store(id="selected-items"),
        dcc.Store(id="undo-redo-actions", data=[0])
    ],
    tabIndex="0",
    style=ROOT_DIV_STYLE,
)
