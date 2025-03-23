from typing import Callable, Dict, Any, Type, Optional, List, Union, Tuple, Collection
from pydantic import BaseModel, create_model, Field, ValidationError
import inspect
import json
from docstring_parser import parse
import importlib
import re
import yaml


class Tools:
    def __init__(self, tools: Optional[List[Callable]] = None):
        self._tools: Dict[str, Dict[str, Any]] = {}
        if tools:
            for tool in tools:
                self._add_tool(tool)

    # Add a tool function with or without a Pydantic model.
    def _add_tool(self, func: Callable, param_model: Optional[Type[BaseModel]] = None):
        """Register a tool function with metadata. If no param_model is provided, infer from function signature."""
        if param_model:
            tool_spec = self._convert_to_tool_spec(func, param_model)
        else:
            tool_spec, param_model = self.__infer_from_signature(func)

        self._tools[func.__name__] = {
            "function": func,
            "param_model": param_model,
            "spec": tool_spec,
        }

    # Return tools in the specified format (default OpenAI).
    def tools(self, format: str = "openai") -> list:
        """Return tools in the specified format (default OpenAI)."""
        if format == "openai":
            return self.__convert_to_openai_format()
        return [tool["spec"] for tool in self._tools.values()]

    # Convert the function and its Pydantic model to a unified tool specification.
    def _convert_to_tool_spec(
        self, func: Callable, param_model: Type[BaseModel]
    ) -> Dict[str, Any]:
        """Convert the function and its Pydantic model to a unified tool specification."""
        type_mapping = {str: "string", int: "integer", float: "number", bool: "boolean"}

        properties = {}
        for field_name, field in param_model.model_fields.items():
            field_type = field.annotation

            # Handle enum types
            if hasattr(field_type, "__members__"):  # Check if it's an enum
                enum_values = [
                    member.value if hasattr(member, "value") else member.name
                    for member in field_type  # type: ignore
                ]
                properties[field_name] = {
                    "type": "string",
                    "enum": enum_values,
                    "description": field.description or "",
                }
                # Convert enum default value to string if it exists
                if str(field.default) != "PydanticUndefined":
                    properties[field_name]["default"] = (
                        field.default.value
                        if hasattr(field.default, "value")
                        else field.default
                    )
            else:
                properties[field_name] = {
                    "type": type_mapping.get(field_type, str(field_type)) if field_type else "any",
                    "description": field.description or "",
                }
                # Add default if it exists and isn't PydanticUndefined
                if str(field.default) != "PydanticUndefined":
                    properties[field_name]["default"] = field.default

        return {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": [
                    name
                    for name, field in param_model.model_fields.items()
                    if field.is_required and str(field.default) == "PydanticUndefined"  # type: ignore
                ],
            },
        }

    def __extract_param_descriptions(self, func: Callable) -> Dict[str, str]:
        """Extract parameter descriptions from function docstring.

        Args:
            func: The function to extract parameter descriptions from

        Returns:
            Dictionary mapping parameter names to their descriptions
        """
        docstring = inspect.getdoc(func) or ""
        parsed_docstring = parse(docstring)

        param_descriptions = {}
        for param in parsed_docstring.params:
            param_descriptions[param.arg_name] = param.description or ""

        return param_descriptions

    def __infer_from_signature(
        self, func: Callable
    ) -> Tuple[Dict[str, Any], Type[BaseModel]]:
        """Infer parameters(required and optional) and requirements directly from the function signature."""
        signature = inspect.signature(func)
        fields: Dict[str, Tuple[Any, Any]] = {}
        required_fields = []

        # Get function's docstring and parse parameter descriptions
        param_descriptions = self.__extract_param_descriptions(func)
        docstring = inspect.getdoc(func) or ""

        # Parse the docstring to get the main function description
        parsed_docstring = parse(docstring)
        function_description = parsed_docstring.short_description or ""
        if parsed_docstring.long_description:
            function_description += "\n\n" + parsed_docstring.long_description

        for param_name, param in signature.parameters.items():
            # Check if a type annotation is missing
            if param.annotation == inspect._empty:
                raise TypeError(
                    f"Parameter '{param_name}' in function '{func.__name__}' must have a type annotation."
                )

            # Determine field type and optionality
            param_type = param.annotation
            description = param_descriptions.get(param_name, "")

            if param.default == inspect._empty:
                fields[param_name] = (param_type, Field(..., description=description))
                required_fields.append(param_name)
            else:
                fields[param_name] = (
                    param_type,
                    Field(default=param.default, description=description),
                )

        # Dynamically create a Pydantic model based on inferred fields
        model_name = f"{func.__name__.capitalize()}Params"
        kwargs = {
            "__module__": func.__module__,
            **fields
        }
        param_model = create_model(model_name, **kwargs)  # type: ignore

        # Convert inferred model to a tool spec format
        tool_spec = self._convert_to_tool_spec(func, param_model)

        # Update the tool spec with the parsed function description instead of raw docstring
        tool_spec["description"] = function_description

        return tool_spec, param_model

    def __convert_to_openai_format(self) -> list:
        """Convert tools to OpenAI's format."""
        return [
            {"type": "function", "function": tool["spec"]}
            for tool in self._tools.values()
        ]

    def results_to_messages(self, results: list, message: Any) -> list:
        """Converts results to messages."""
        # if message is empty return empty list
        if not message or len(results) == 0:
            return []

        messages = []
        # Iterate over results and match with tool calls from the message
        for result in results:
            # Find matching tool call from message.tool_calls
            for tool_call in message.tool_calls:
                if tool_call.id == result["tool_call_id"]:
                    messages.append(
                        {
                            "role": "tool",
                            "name": result["name"],
                            "content": json.dumps(result["content"]),
                            "tool_call_id": tool_call.id,
                        }
                    )
                    break

        return messages

    def execute(self, tool_calls) -> list:
        """Executes registered tools based on the tool calls from the model.

        Args:
            tool_calls: List of tool calls from the model

        Returns:
            List of results from executing each tool call
        """
        results = []

        # Handle single tool call or list of tool calls
        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]

        for tool_call in tool_calls:
            # Handle both dictionary and object-style tool calls
            if isinstance(tool_call, dict):
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
            else:
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

            # Ensure arguments is a dict
            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            if tool_name not in self._tools:
                raise ValueError(f"Tool '{tool_name}' not registered.")

            tool = self._tools[tool_name]
            tool_func = tool["function"]
            param_model = tool["param_model"]

            # Validate and parse the arguments with Pydantic if a model exists
            try:
                validated_args = param_model(**arguments)
                result = tool_func(**validated_args.model_dump())
                results.append(result)
            except ValidationError as e:
                raise ValueError(f"Error in tool '{tool_name}' parameters: {e}")

        return results

    def execute_tool(self, tool_calls) -> tuple[list, list]:
        """Executes registered tools based on the tool calls from the model.

        Args:
            tool_calls: List of tool calls from the model

        Returns:
            List of tuples containing (result, result_message) for each tool call
        """
        results = []
        messages = []

        # Handle single tool call or list of tool calls
        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]

        for tool_call in tool_calls:
            # Handle both dictionary and object-style tool calls
            if isinstance(tool_call, dict):
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
                tool_call_id = tool_call["id"]
            else:
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments
                tool_call_id = tool_call.id

            # Ensure arguments is a dict
            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            if tool_name not in self._tools:
                raise ValueError(f"Tool '{tool_name}' not registered.")

            tool = self._tools[tool_name]
            tool_func = tool["function"]
            param_model = tool["param_model"]

            # Validate and parse the arguments with Pydantic if a model exists
            try:
                validated_args = param_model(**arguments)
                result = tool_func(**validated_args.model_dump())
                results.append(result)
                messages.append(
                    {
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(result),
                        "tool_call_id": tool_call_id,
                    }
                )
            except ValidationError as e:
                raise ValueError(f"Error in tool '{tool_name}' parameters: {e}")

        return results, messages


def get_class_qualname(cls):
    """Get the qualified name of a class."""
    return f"{cls.__module__}.{cls.__qualname__}"


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load a yaml file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except Exception as e:
        print(f"Error loading yaml file {file_path}: {e}")
        return {}


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def import_module(module_name: str) -> Any:
    """Import a module dynamically."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def is_valid_proxy_url(proxy: Optional[str]) -> bool:
    """Validate proxy URL format."""
    if not proxy:
        return False
    
    # 验证代理URL格式
    pattern = r"^(http|https|socks5)://([^:]+:[^@]+@)?[^:]+:\d+/?$"
    return bool(re.match(pattern, proxy))
