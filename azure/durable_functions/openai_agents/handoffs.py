#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
"""Handoff conversion utilities for Azure Durable Functions OpenAI agent operations."""

from typing import Any

from agents import Handoff
from pydantic import BaseModel


class DurableHandoff(BaseModel):
    """Serializable representation of a Handoff.

    Contains only the data needed by the model execution to
    determine what to handoff to, not the actual handoff invocation.
    """

    tool_name: str
    tool_description: str
    input_json_schema: dict[str, Any]
    agent_name: str
    strict_json_schema: bool = True

    @classmethod
    def from_handoff(cls, handoff: Handoff) -> "DurableHandoff":
        """Create a DurableHandoff from an OpenAI agent Handoff.

        This method converts OpenAI agent Handoff instances into serializable
        DurableHandoff objects for use within Azure Durable Functions.

        Parameters
        ----------
        handoff : Handoff
            The OpenAI agent Handoff to convert

        Returns
        -------
        DurableHandoff
            A serializable handoff representation
        """
        return cls(
            tool_name=handoff.tool_name,
            tool_description=handoff.tool_description,
            input_json_schema=handoff.input_json_schema,
            agent_name=handoff.agent_name,
            strict_json_schema=handoff.strict_json_schema,
        )

    def to_handoff(self) -> Handoff[Any, Any]:
        """Create an OpenAI agent Handoff instance from this DurableHandoff.

        This method converts the serializable DurableHandoff back into an
        OpenAI agent Handoff instance for execution.

        Returns
        -------
        Handoff
            OpenAI agent Handoff instance
        """
        return Handoff(
            tool_name=self.tool_name,
            tool_description=self.tool_description,
            input_json_schema=self.input_json_schema,
            agent_name=self.agent_name,
            strict_json_schema=self.strict_json_schema,
            on_invoke_handoff=lambda ctx, input: None,
        )
