import os
import sys
import importlib
import inspect
import re
import ast
import dash_bootstrap_components as dbc  # type: ignore
import dash_daq as daq  # type: ignore
from dash_extensions.enrich import html  # type: ignore
from typing import Any, Optional, Type
from type_aliases import (
    Graph,
    GraphFunction,
    GraphOrNone,
    InputComponent,
    InputValue,
)


class DocError(ValueError):
    """Raised when the __doc__ attribute of an object is badly written."""

    pass


# get the absolute path of the current directory
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
FOLDER_NAME = "graph_templates"
# join the current directory with the folder name
DIRECTORY = os.path.join(CURRENT_DIR, FOLDER_NAME)
sys.path.append(DIRECTORY)
FUNCTION_DICT = {}

for filename in os.listdir(DIRECTORY):
    if os.path.isfile(os.path.join(DIRECTORY, filename)) and filename.endswith(".py"):
        module_name = filename[:-3]  # remove the .py extension
        module = importlib.import_module(module_name)
        function = getattr(module, module_name)
        FUNCTION_DICT[module_name] = function


def dropdown_functions(function_dict: dict[str, GraphFunction]) -> list[dict[str, str]]:
    dropdown_options = []
    for key, item in function_dict.items():
        doc = inspect.getdoc(item)
        if doc is None or not is_function_typed(item):
            continue
        match = re.search(r"(.+?)\n", doc)
        if not match:
            raise DocError(f"Invalid name of function {key} for UI")
        name = match.group(1)
        dropdown_options.append({"label": name, "value": key})
    return dropdown_options


def is_function_typed(function: GraphFunction) -> bool:
    sig = inspect.signature(function)
    if sig.return_annotation == inspect.Parameter.empty:
        return False
    for _, value in sig.parameters.items():
        if value.annotation == inspect.Parameter.empty:
            return False
    return True


def handle_yaml_graph(networkx_data: dict) -> GraphOrNone:
    networkx_data = networkx_data.get("graph_params", None)
    if networkx_data is None:
        print("Bad yaml file")
        return None
    if networkx_data.get("loader") == "hardcodedxx":
        # different handling
        return networkx_data
    loader_function = FUNCTION_DICT[networkx_data["loader"]]
    print(inspect.signature(loader_function).parameters)
    print(networkx_data["loader_params"])
    graph = call_graph_function_with_params(
        loader_function, networkx_data["loader_params"]
    )
    return graph


def call_graph_function_with_params(
    func_reference: GraphFunction, param_dict: dict[str, Any]
) -> Graph:
    params = inspect.signature(func_reference).parameters  # get function parameters
    kwargs = {}
    for name, param in params.items():
        if name in param_dict:
            # use parameter value from dictionary
            kwargs[name] = param_dict[name]
        elif param.default is not inspect.Parameter.empty:
            # use default value for optional parameter
            kwargs[name] = param.default
        else:
            # parameter is required but not present in dictionary
            raise ValueError(f"Missing required parameter '{name}'")
    return func_reference(**kwargs)  # call the function with the extracted arguments


def handle_input_dict(input_dict: dict) -> tuple[str, InputValue]:
    if input_dict["type"] == "BooleanSwitch":
        value = input_dict["props"]["on"]
    elif input_dict["props"]["type"] == "number":
        value = input_dict["props"]["value"]
    else:
        value = ast.literal_eval(input_dict["props"]["value"])
    name = input_dict["props"]["id"]
    return name, value


def create_function_parameter_input_field(
    parameter_name: str,
    parameter_type: Type,
    function: GraphFunction,
) -> InputComponent:
    params = inspect.signature(function).parameters
    required = params[parameter_name].default is inspect.Parameter.empty
    default = ""
    if not required:
        default = params[parameter_name].default

    if (
        parameter_type == int
        or parameter_type == float
        or parameter_type == Optional[int]
        or parameter_type == Optional[float]
    ):
        return dbc.Input(
            id=parameter_name,
            type="number",
            min=0,
            required=required,
            value=default,
            className="input",
        )
    elif parameter_type == bool:
        if default == "":
            return daq.BooleanSwitch(id=parameter_name, on=False, className="input")
        return daq.BooleanSwitch(id=parameter_name, on=default)
    elif (
        parameter_type == dict
        or parameter_type == Optional[dict]
        or parameter_type == Optional[list]
        or parameter_type == list
        or parameter_type == set
        or parameter_type == Optional[set]
    ):
        return dbc.Input(
            id=parameter_name,
            type="text",
            required=required,
            value=str(default),
            className="label",
        )
    else:
        return html.Label("Unknown parameter type in function")
