#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
"""Tool conversion utilities for Azure Durable Functions OpenAI agent operations."""

from typing import Any, Union

from agents import (
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    HostedMCPTool,
    ImageGenerationTool,
    Tool,
    UserError,
    WebSearchTool,
)
from openai.types.responses.tool_param import Mcp
from pydantic import BaseModel


# Built-in tool types that can be serialized directly without conversion
BUILT_IN_TOOL_TYPES = (
    FileSearchTool,
    WebSearchTool,
    ImageGenerationTool,
    CodeInterpreterTool,
)


class DurableFunctionTool(BaseModel):
    """Serializable representation of a FunctionTool.

    Contains only the data needed by the model execution to
    determine what tool to call, not the actual tool invocation.
    """

    name: str
    description: str
    params_json_schema: dict[str, Any]
    strict_json_schema: bool = True


class DurableMCPToolConfig(BaseModel):
    """Serializable representation of a HostedMCPTool.

    Contains only the data needed by the model execution to
    determine what tool to call, not the actual tool invocation.
    """

    tool_config: Mcp


DurableTool = Union[
    DurableFunctionTool,
    FileSearchTool,
    WebSearchTool,
    ImageGenerationTool,
    CodeInterpreterTool,
    DurableMCPToolConfig,
]


def create_tool_from_durable_tool(
    durable_tool: DurableTool,
) -> Tool:
    """Convert a DurableTool to an OpenAI agent Tool for execution.

    This function transforms Durable Functions tool definitions into actual
    OpenAI agent Tool instances that can be used during model execution.

    Parameters
    ----------
    durable_tool : DurableTool
        The Durable tool definition to convert

    Returns
    -------
    Tool
        An OpenAI agent Tool instance ready for execution

    Raises
    ------
    UserError
        If the tool type is not supported
    """
    # Built-in tools that don't need conversion
    if isinstance(durable_tool, BUILT_IN_TOOL_TYPES):
        return durable_tool

    # Convert Durable MCP tool configuration to HostedMCPTool
    if isinstance(durable_tool, DurableMCPToolConfig):
        return HostedMCPTool(
            tool_config=durable_tool.tool_config,
        )

    # Convert Durable function tool to FunctionTool
    if isinstance(durable_tool, DurableFunctionTool):
        return FunctionTool(
            name=durable_tool.name,
            description=durable_tool.description,
            params_json_schema=durable_tool.params_json_schema,
            on_invoke_tool=lambda ctx, input: "",
            strict_json_schema=durable_tool.strict_json_schema,
        )

    raise UserError(f"Unsupported tool type: {durable_tool}")


def convert_tool_to_durable_tool(tool: Tool) -> DurableTool:
    """Convert an OpenAI agent Tool to a DurableTool for serialization.

    This function transforms OpenAI agent Tool instances into Durable Functions
    tool definitions that can be serialized and passed to activities.

    Parameters
    ----------
    tool : Tool
        The OpenAI agent Tool to convert

    Returns
    -------
    DurableTool
        A serializable tool definition

    Raises
    ------
    ValueError
        If the tool type is not supported for conversion
    """
    # Built-in tools that can be serialized directly
    if isinstance(tool, BUILT_IN_TOOL_TYPES):
        return tool

    # Convert HostedMCPTool to Durable MCP configuration
    elif isinstance(tool, HostedMCPTool):
        return DurableMCPToolConfig(tool_config=tool.tool_config)

    # Convert FunctionTool to Durable function tool
    elif isinstance(tool, FunctionTool):
        return DurableFunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=tool.params_json_schema,
            strict_json_schema=tool.strict_json_schema,
        )

    else:
        raise ValueError(f"Unsupported tool type for Durable Functions: {type(tool).__name__}")
