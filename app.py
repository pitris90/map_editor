"""BSD 3-Clause License

Copyright (c) 2023, pitris90

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import dash_bootstrap_components as dbc  # type: ignore
from html_layout import APP_LAYOUT
from dash_extensions.enrich import (  # type: ignore
    DashProxy,
    MultiplexerTransform
)


# selected_items = Selected_items()

app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    transforms=[MultiplexerTransform()],
    suppress_callback_exceptions=True,
)

app.layout = APP_LAYOUT


# TEST CALLBACK FUNCTION
# @app.callback(
#     Output("output-data-upload", "children"),
#     [
#         Input("main-debug-button", "n_clicks"),
#         State("graph-cytoscape", "elements"),
#         State("graph-cytoscape", "tapNode"),
#         State("graph-cytoscape", "selectedNodeData"),
#         State("graph-cytoscape", "selectedEdgeData"),
#         State("graph-cytoscape", "stylesheet"),
#         State("graph-cytoscape", "ele_move_pos"),
#     ],
# )
# def test_graph(
#     n: Optional[int],
#     elements: GraphElements,
#     tapNode: Any,
#     node_data: list,
#     edge_data: list,
#     stylesheet: list,
#     new_posiiton: Any,
# ) -> str:
#     if n:
#         print(elements)
#         print("\n")
#         print(node_data)
#         print("\n")
#         print(edge_data)
#         return "Klik"
#     return "Neklik"


if __name__ == "__main__":
    app.run_server(debug=False)
