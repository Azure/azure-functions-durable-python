#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import enum
import json
from typing import Any, AsyncIterator, Optional, Union, cast

from azure.durable_functions.models.RetryOptions import RetryOptions
from pydantic import BaseModel, Field
from agents import (
    AgentOutputSchema,
    AgentOutputSchemaBase,
    Handoff,
    Model,
    ModelProvider,
    ModelResponse,
    ModelSettings,
    ModelTracing,
    OpenAIProvider,
    Tool,
    TResponseInputItem,
    UserError,
)
from agents.items import TResponseStreamEvent
from openai.types.responses.response_prompt_param import ResponsePromptParam

from .task_tracker import TaskTracker
from .tools import (
    DurableTool,
    create_tool_from_durable_tool,
    convert_tool_to_durable_tool,
)
from .handoffs import DurableHandoff


class DurableAgentOutputSchema(AgentOutputSchemaBase, BaseModel):
    """Serializable representation of agent output schema."""

    output_type_name: Optional[str] = None
    output_schema: Optional[dict[str, Any]] = None
    strict_json_schema: bool

    def is_plain_text(self) -> bool:
        """Whether the output type is plain text (versus a JSON object)."""
        return self.output_type_name in (None, "str")

    def name(self) -> str:
        """Get the name of the output type."""
        if self.output_type_name is None:
            raise ValueError("Output type name has not been specified")
        return self.output_type_name

    def json_schema(self) -> dict[str, Any]:
        """Return the JSON schema of the output.

        Will only be called if the output type is not plain text.
        """
        if self.is_plain_text():
            raise UserError("Cannot provide JSON schema for plain text output types")
        if self.output_schema is None:
            raise UserError("Output schema definition is missing")
        return self.output_schema

    def is_strict_json_schema(self) -> bool:
        """Check if the JSON schema is in strict mode.

        Strict mode constrains the JSON schema features, but guarantees valid JSON.
        See here for details:
        https://platform.openai.com/docs/guides/structured-outputs#supported-schemas
        """
        return self.strict_json_schema

    def validate_json(self, json_str: str) -> Any:
        """Validate a JSON string against the output type.

        You must return the validated object, or raise a `ModelBehaviorError` if
        the JSON is invalid.
        """
        raise NotImplementedError()


class ModelTracingLevel(enum.IntEnum):
    """Serializable IntEnum representation of ModelTracing for Azure Durable Functions.

    Values must match ModelTracing from the OpenAI SDK. This separate enum is required
    because ModelTracing is a standard Enum while Pydantic serialization requires IntEnum
    for proper JSON serialization in activity inputs.
    """

    DISABLED = 0
    ENABLED = 1
    ENABLED_WITHOUT_DATA = 2


class DurableModelActivityInput(BaseModel):
    """Serializable input for the durable model invocation activity."""

    input: Union[str, list[TResponseInputItem]]
    model_settings: ModelSettings
    tracing: ModelTracingLevel
    model_name: Optional[str] = None
    system_instructions: Optional[str] = None
    tools: list[DurableTool] = Field(default_factory=list)
    output_schema: Optional[DurableAgentOutputSchema] = None
    handoffs: list[DurableHandoff] = Field(default_factory=list)
    previous_response_id: Optional[str] = None
    prompt: Optional[Any] = None

    def to_json(self) -> str:
        """Convert to a JSON string."""
        try:
            return self.model_dump_json(warnings=False)
        except Exception:
            # Fallback to basic JSON serialization
            try:
                return json.dumps(self.model_dump(warnings=False), default=str)
            except Exception as fallback_error:
                raise ValueError(
                    f"Unable to serialize DurableModelActivityInput: {fallback_error}"
                ) from fallback_error

    @classmethod
    def from_json(cls, json_str: str) -> 'DurableModelActivityInput':
        """Create from a JSON string."""
        return cls.model_validate_json(json_str)


class ModelInvoker:
    """Handles OpenAI model invocations for Durable Functions activities."""

    def __init__(self, model_provider: Optional[ModelProvider] = None):
        """Initialize the activity with a model provider."""
        self._model_provider = model_provider or OpenAIProvider()

    async def invoke_model_activity(self, input: DurableModelActivityInput) -> ModelResponse:
        """Activity that invokes a model with the given input."""
        model = self._model_provider.get_model(input.model_name)

        # Avoid https://github.com/pydantic/pydantic/issues/9541
        normalized_input = json.loads(json.dumps(input.input, default=str))

        # Convert durable tools to agent tools
        tools = [
            create_tool_from_durable_tool(durable_tool)
            for durable_tool in input.tools
        ]

        # Convert handoff descriptors to agent handoffs
        handoffs = [
            durable_handoff.to_handoff()
            for durable_handoff in input.handoffs
        ]

        return await model.get_response(
            system_instructions=input.system_instructions,
            input=normalized_input,
            model_settings=input.model_settings,
            tools=tools,
            output_schema=input.output_schema,
            handoffs=handoffs,
            tracing=ModelTracing(input.tracing),
            previous_response_id=input.previous_response_id,
            prompt=input.prompt,
        )


class DurableActivityModel(Model):
    """A model implementation that uses durable activities for model invocations."""

    def __init__(
        self,
        model_name: Optional[str],
        task_tracker: TaskTracker,
        retry_options: Optional[RetryOptions],
        activity_name: str,
    ) -> None:
        self.model_name = model_name
        self.task_tracker = task_tracker
        self.retry_options = retry_options
        self.activity_name = activity_name

    async def get_response(
        self,
        system_instructions: Optional[str],
        input: Union[str, list[TResponseInputItem]],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: Optional[AgentOutputSchemaBase],
        handoffs: list[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: Optional[str],
        prompt: Optional[ResponsePromptParam],
        conversation_id: Optional[str] = None,
    ) -> ModelResponse:
        """Get a response from the model."""
        # Convert agent tools to Durable tools
        durable_tools = [convert_tool_to_durable_tool(tool) for tool in tools]

        # Convert agent handoffs to Durable handoff descriptors
        durable_handoffs = [DurableHandoff.from_handoff(handoff) for handoff in handoffs]
        if output_schema is not None and not isinstance(
            output_schema, AgentOutputSchema
        ):
            raise TypeError(
                f"Only AgentOutputSchema is supported by Durable Model, "
                f"got {type(output_schema).__name__}"
            )

        output_schema_input = (
            None
            if output_schema is None
            else DurableAgentOutputSchema(
                output_type_name=output_schema.name(),
                output_schema=(
                    output_schema.json_schema()
                    if not output_schema.is_plain_text()
                    else None
                ),
                strict_json_schema=output_schema.is_strict_json_schema(),
            )
        )

        activity_input = DurableModelActivityInput(
            model_name=self.model_name,
            system_instructions=system_instructions,
            input=cast(Union[str, list[TResponseInputItem]], input),
            model_settings=model_settings,
            tools=durable_tools,
            output_schema=output_schema_input,
            handoffs=durable_handoffs,
            tracing=ModelTracingLevel.DISABLED,  # ModelTracingLevel(tracing.value),
            previous_response_id=previous_response_id,
            prompt=prompt,
        )

        activity_input_json = activity_input.to_json()

        if self.retry_options:
            response = self.task_tracker.get_activity_call_result_with_retry(
                self.activity_name,
                self.retry_options,
                activity_input_json,
            )
        else:
            response = self.task_tracker.get_activity_call_result(
                self.activity_name,
                activity_input_json
            )

        json_response = json.loads(response)
        model_response = ModelResponse(**json_response)
        return model_response

    def stream_response(
        self,
        system_instructions: Optional[str],
        input: Union[str, list[TResponseInputItem]],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: Optional[AgentOutputSchemaBase],
        handoffs: list[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: Optional[str],
        prompt: Optional[ResponsePromptParam],
    ) -> AsyncIterator[TResponseStreamEvent]:
        """Stream a response from the model."""
        raise NotImplementedError("Durable model doesn't support streams yet")
