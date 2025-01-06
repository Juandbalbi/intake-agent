from __future__ import annotations

import json
import os
from collections.abc import Sequence
from copy import deepcopy
from typing import Any, Optional

from pydantic import BaseModel, Field, create_model

from src.models.agent import Agent, FormField
from src.models.streaming import ToolCall
from src.utils.constants import AGENT_DB_FILE, FIELD_TYPES_MAPPER


def load_agents(as_dict: bool = False) -> list[Agent] | dict:
    if os.path.exists(AGENT_DB_FILE):
        with open(AGENT_DB_FILE, "r") as f:
            try:
                agents = json.load(f)
                return [Agent(**agent) for agent in agents] if not as_dict else agents
            except json.JSONDecodeError:
                return []
    return []


def save_agent(agent_data: dict) -> None:
    agents = load_agents(as_dict=True)
    agents.append(agent_data)

    with open(AGENT_DB_FILE, "w") as f:
        json.dump(agents, f, indent=2)


def model_fields_to_string(model: type[BaseModel]) -> str:
    """
    Returns a string representation of the model's fields in a text friendly format.

    Returns:
        str: A string representation of the model's fields.
    """

    fields_string = ""
    for field_name, field_info in model.model_fields.items():
        field_name = field_info.title if field_info.title else field_name
        field_desc = (
            f"- {field_name} - ({field_info.annotation}): "
            f"{field_info.description}\n"
        )
        fields_string += field_desc

    return fields_string


def _rm_titles(kv: dict, prev_key: str = "") -> dict:
    new_kv = {}
    for k, v in kv.items():
        if k == "title":
            if isinstance(v, dict) and prev_key == "properties" and "title" in v:
                new_kv[k] = _rm_titles(v, k)
            else:
                continue
        elif isinstance(v, dict):
            new_kv[k] = _rm_titles(v, k)
        else:
            new_kv[k] = v
    return new_kv


def _retrieve_ref(path: str, schema: dict) -> dict:
    components = path.split("/")
    if components[0] != "#":
        msg = (
            "ref paths are expected to be URI fragments, meaning they should start "
            "with #."
        )
        raise ValueError(msg)
    out = schema
    for component in components[1:]:
        if component in out:
            out = out[component]
        elif component.isdigit() and int(component) in out:
            out = out[int(component)]
        else:
            msg = f"Reference '{path}' not found."
            raise KeyError(msg)
    return deepcopy(out)


def _dereference_refs_helper(
    obj: Any,
    full_schema: dict[str, Any],
    skip_keys: Sequence[str],
    processed_refs: Optional[set[str]] = None,
) -> Any:
    if processed_refs is None:
        processed_refs = set()

    if isinstance(obj, dict):
        obj_out = {}
        for k, v in obj.items():
            if k in skip_keys:
                obj_out[k] = v
            elif k == "$ref":
                if v in processed_refs:
                    continue
                processed_refs.add(v)
                ref = _retrieve_ref(v, full_schema)
                full_ref = _dereference_refs_helper(
                    ref, full_schema, skip_keys, processed_refs
                )
                processed_refs.remove(v)
                return full_ref
            elif isinstance(v, (list, dict)):
                obj_out[k] = _dereference_refs_helper(
                    v, full_schema, skip_keys, processed_refs
                )
            else:
                obj_out[k] = v
        return obj_out
    elif isinstance(obj, list):
        return [
            _dereference_refs_helper(el, full_schema, skip_keys, processed_refs)
            for el in obj
        ]
    else:
        return obj


def _infer_skip_keys(
    obj: Any, full_schema: dict, processed_refs: Optional[set[str]] = None
) -> list[str]:
    if processed_refs is None:
        processed_refs = set()

    keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref":
                if v in processed_refs:
                    continue
                processed_refs.add(v)
                ref = _retrieve_ref(v, full_schema)
                keys.append(v.split("/")[1])
                keys += _infer_skip_keys(ref, full_schema, processed_refs)
            elif isinstance(v, (list, dict)):
                keys += _infer_skip_keys(v, full_schema, processed_refs)
    elif isinstance(obj, list):
        for el in obj:
            keys += _infer_skip_keys(el, full_schema, processed_refs)
    return keys


def dereference_refs(
    schema_obj: dict,
    *,
    full_schema: Optional[dict] = None,
    skip_keys: Optional[Sequence[str]] = None,
) -> dict:
    """Try to substitute $refs in JSON Schema.

    Args:
        schema_obj: The schema object to dereference.
        full_schema: The full schema object. Defaults to None.
        skip_keys: The keys to skip. Defaults to None.

    Returns:
        The dereferenced schema object.
    """

    full_schema = full_schema or schema_obj
    skip_keys = (
        skip_keys
        if skip_keys is not None
        else _infer_skip_keys(schema_obj, full_schema)
    )
    return _dereference_refs_helper(schema_obj, full_schema, skip_keys)


def convert_pydantic_to_openai_function(
    model: type[BaseModel],
    *,
    rm_titles: bool = True,
) -> dict[str, Any]:
    """Converts a Pydantic model to a function description for the OpenAI API.

    Args:
        model: The Pydantic model to convert.
        name: The name of the function. If not provided, the title of the schema will be
            used.
        description: The description of the function. If not provided, the description
            of the schema will be used.
        rm_titles: Whether to remove titles from the schema. Defaults to True.

    Returns:
        The function description.
    """
    schema = model.model_json_schema()  # Pydantic 2
    schema = dereference_refs(schema)
    if "definitions" in schema:  # pydantic 1
        schema.pop("definitions", None)
    if "$defs" in schema:  # pydantic 2
        schema.pop("$defs", None)
    title = schema.pop("title", "")
    description = schema.pop("description", "")
    return {
        "name": title,
        "description": description,
        "parameters": _rm_titles(schema) if rm_titles else schema,
    }


def convert_pydantic_to_openai_tool(
    model: type[BaseModel],
) -> dict[str, Any]:
    """Converts a Pydantic model to a function description for the OpenAI API.

    Args:
        model: The Pydantic model to convert.
        name: The name of the function. If not provided, the title of the schema will be
            used.
        description: The description of the function. If not provided, the description
            of the schema will be used.

    Returns:
        The tool description.
    """

    return {
        "type": "function",
        "function": convert_pydantic_to_openai_function(model),
    }


def fetch_form_data(tool_calls: list[ToolCall], model: type[BaseModel]) -> dict:
    for tool_call in tool_calls:
        if tool_call.function.name == model.__name__:
            return json.loads(tool_call.function.arguments)
    return {}


def create_dynamic_model(fields: list[FormField]) -> type[BaseModel]:
    field_definitions = {}
    for field in fields:
        python_type = FIELD_TYPES_MAPPER[field.type]
        field_definitions[field.name.lower().replace(" ", "_")] = (
            python_type,
            Field(
                description=field.description,
                example=field.example if field.example else None,
            ),
        )

    return create_model("SubmitIntake", **field_definitions)
