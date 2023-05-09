import networkx as nx  # type: ignore
from dash_extensions.enrich import html  # type: ignore
import dash_bootstrap_components as dbc # type: ignore
import dash_daq as daq  # type: ignore
from typing import Callable, Any, Union, Optional

Graph = Union[nx.Graph, nx.DiGraph]
GraphFunction = Callable[..., Graph]
GraphOrNone = Optional[Graph]
GraphElements = list[dict[str, Any]]
GraphElement = dict[str, Any]
InputComponent = Union[html.Label, dbc.Input, daq.BooleanSwitch]
InputValue = Union[bool, str, dict, int, float]