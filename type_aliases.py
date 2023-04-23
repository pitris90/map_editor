import networkx as nx  # type: ignore
from dash_extensions.enrich import html, dcc  # type: ignore
import dash_daq as daq  # type: ignore
from typing import List, Dict, Callable, Any, Union, Optional

Graph = Union[nx.Graph, nx.DiGraph]
GraphFunction = Callable[..., Graph]
GraphOrNone = Optional[Graph]
GraphElements = List[Dict[str, Any]]
InputComponent = Union[html.Label, dcc.Input, daq.BooleanSwitch]
