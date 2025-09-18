import enum
import json
import logging
from typing import Any, AsyncIterator, Optional, Union, cast

from azure.durable_functions.models.RetryOptions import RetryOptions
from pydantic import BaseModel, Field
from agents import (
    AgentOutputSchema,
    AgentOutputSchemaBase,
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    Handoff,
    HostedMCPTool,
    ImageGenerationTool,
    Model,
    ModelProvider,
    ModelResponse,
    ModelSettings,
    ModelTracing,
    OpenAIProvider,
    RunContextWrapper,
    Tool,
    TResponseInputItem,
    UserError,
    WebSearchTool,
)
from agents.items import TResponseStreamEvent
from openai.types.responses.tool_param import Mcp
from openai.types.responses.response_prompt_param import ResponsePromptParam

from .task_tracker import TaskTracker

try:
    from azure.durable_functions import ApplicationError
except ImportError:
    # Fallback if ApplicationError is not available
    class ApplicationError(Exception):
        """Custom application error for handling retryable and non-retryable errors."""

        def __init__(self, message: str, non_retryable: bool = False, next_retry_delay=None):
            super().__init__(message)
            self.non_retryable = non_retryable
            self.next_retry_delay = next_retry_delay

logger = logging.getLogger(__name__)


class HandoffInput(BaseModel):
    """Data conversion friendly representation of a Handoff.

    Contains only the fields which are needed by the model execution to
    determine what to handoff to, not the actual handoff invocation,
    which remains in the workflow context.
    """

    tool_name: str
    tool_description: str
    input_json_schema: dict[str, Any]
    agent_name: str
    strict_json_schema: bool = True


class FunctionToolInput(BaseModel):
    """Data conversion friendly representation of a FunctionTool.

    Contains only the fields which are needed by the model execution to
    determine what tool to call, not the actual tool invocation,
    which remains in the workflow context.
    """

    name: str
    description: str
    params_json_schema: dict[str, Any]
    strict_json_schema: bool = True


class HostedMCPToolInput(BaseModel):
    """Data conversion friendly representation of a HostedMCPTool.

    Contains only the fields which are needed by the model execution to
    determine what tool to call, not the actual tool invocation,
    which remains in the workflow context.
    """

    tool_config: Mcp


ToolInput = Union[
    FunctionToolInput,
    FileSearchTool,
    WebSearchTool,
    ImageGenerationTool,
    CodeInterpreterTool,
    HostedMCPToolInput,
]


class AgentOutputSchemaInput(AgentOutputSchemaBase, BaseModel):
    """Data conversion friendly representation of AgentOutputSchema."""

    output_type_name: Optional[str] = None
    is_wrapped: bool
    output_schema: Optional[dict[str, Any]] = None
    strict_json_schema: bool

    def is_plain_text(self) -> bool:
        """Whether the output type is plain text (versus a JSON object)."""
        return self.output_type_name is None or self.output_type_name == "str"

    def is_strict_json_schema(self) -> bool:
        """Whether the JSON schema is in strict mode."""
        return self.strict_json_schema

    def json_schema(self) -> dict[str, Any]:
        """Get the JSON schema of the output type."""
        if self.is_plain_text():
            raise UserError("Output type is plain text, so no JSON schema is available")
        if self.output_schema is None:
            raise UserError("Output schema is not defined")
        return self.output_schema

    def validate_json(self, json_str: str) -> Any:
        """Validate the JSON string against the schema."""
        raise NotImplementedError()

    def name(self) -> str:
        """Get the name of the output type."""
        if self.output_type_name is None:
            raise ValueError("output_type_name is None")
        return self.output_type_name


class ModelTracingInput(enum.IntEnum):
    """Conversion friendly representation of ModelTracing.

    Needed as ModelTracing is enum.Enum instead of IntEnum
    """

    DISABLED = 0
    ENABLED = 1
    ENABLED_WITHOUT_DATA = 2


class ActivityModelInput(BaseModel):
    """Input for the invoke_model_activity activity."""

    input: Union[str, list[TResponseInputItem]]
    model_settings: ModelSettings
    tracing: ModelTracingInput
    model_name: Optional[str] = None
    system_instructions: Optional[str] = None
    tools: list[ToolInput] = Field(default_factory=list)
    output_schema: Optional[AgentOutputSchemaInput] = None
    handoffs: list[HandoffInput] = Field(default_factory=list)
    previous_response_id: Optional[str] = None
    prompt: Optional[Any] = None

    def to_json(self) -> str:
        """Convert the ActivityModelInput to a JSON string."""
        try:
            return self.model_dump_json(warnings=False)
        except Exception:
            # Fallback to basic JSON serialization
            try:
                return json.dumps(self.model_dump(warnings=False), default=str)
            except Exception as fallback_error:
                raise ValueError(
                    f"Unable to serialize ActivityModelInput: {fallback_error}"
                ) from fallback_error

    @classmethod
    def from_json(cls, json_str: str) -> 'ActivityModelInput':
        """Create an ActivityModelInput instance from a JSON string."""
        return cls.model_validate_json(json_str)


class ModelInvoker:
    """Handles OpenAI model invocations for Durable Functions activities."""

    def __init__(self, model_provider: Optional[ModelProvider] = None):
        """Initialize the activity with a model provider."""
        self._model_provider = model_provider or OpenAIProvider()

    async def invoke_model_activity(self, input: ActivityModelInput) -> ModelResponse:
        """Activity that invokes a model with the given input."""
        model = self._model_provider.get_model(input.model_name)

        async def empty_on_invoke_tool(ctx: RunContextWrapper[Any], input: str) -> str:
            return ""

        async def empty_on_invoke_handoff(
            ctx: RunContextWrapper[Any], input: str
        ) -> Any:
            return None

        # workaround for https://github.com/pydantic/pydantic/issues/9541
        # ValidatorIterator returned
        input_json = json.dumps(input.input, default=str)
        input_input = json.loads(input_json)

        def make_tool(tool: ToolInput) -> Tool:
            if isinstance(
                tool,
                (
                    FileSearchTool,
                    WebSearchTool,
                    ImageGenerationTool,
                    CodeInterpreterTool,
                ),
            ):
                return tool
            elif isinstance(tool, HostedMCPToolInput):
                return HostedMCPTool(
                    tool_config=tool.tool_config,
                )
            elif isinstance(tool, FunctionToolInput):
                return FunctionTool(
                    name=tool.name,
                    description=tool.description,
                    params_json_schema=tool.params_json_schema,
                    on_invoke_tool=empty_on_invoke_tool,
                    strict_json_schema=tool.strict_json_schema,
                )
            else:
                raise UserError(f"Unknown tool type: {tool.name}")

        tools = [make_tool(x) for x in input.tools]
        handoffs: list[Handoff[Any, Any]] = [
            Handoff(
                tool_name=x.tool_name,
                tool_description=x.tool_description,
                input_json_schema=x.input_json_schema,
                agent_name=x.agent_name,
                strict_json_schema=x.strict_json_schema,
                on_invoke_handoff=empty_on_invoke_handoff,
            )
            for x in input.handoffs
        ]

        return await model.get_response(
            system_instructions=input.system_instructions,
            input=input_input,
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
        def make_tool_info(tool: Tool) -> ToolInput:
            if isinstance(
                tool,
                (
                    FileSearchTool,
                    WebSearchTool,
                    ImageGenerationTool,
                    CodeInterpreterTool,
                ),
            ):
                return tool
            elif isinstance(tool, HostedMCPTool):
                return HostedMCPToolInput(tool_config=tool.tool_config)
            elif isinstance(tool, FunctionTool):
                return FunctionToolInput(
                    name=tool.name,
                    description=tool.description,
                    params_json_schema=tool.params_json_schema,
                    strict_json_schema=tool.strict_json_schema,
                )
            else:
                raise ValueError(f"Unsupported tool type: {tool.name}")

        tool_infos = [make_tool_info(x) for x in tools]
        handoff_infos = [
            HandoffInput(
                tool_name=x.tool_name,
                tool_description=x.tool_description,
                input_json_schema=x.input_json_schema,
                agent_name=x.agent_name,
                strict_json_schema=x.strict_json_schema,
            )
            for x in handoffs
        ]
        if output_schema is not None and not isinstance(
            output_schema, AgentOutputSchema
        ):
            raise TypeError(
                f"Only AgentOutputSchema is supported by Durable Model, "
                f"got {type(output_schema).__name__}"
            )
        agent_output_schema = output_schema
        output_schema_input = (
            None
            if agent_output_schema is None
            else AgentOutputSchemaInput(
                output_type_name=agent_output_schema.name(),
                is_wrapped=agent_output_schema._is_wrapped,
                output_schema=agent_output_schema.json_schema()
                if not agent_output_schema.is_plain_text()
                else None,
                strict_json_schema=agent_output_schema.is_strict_json_schema(),
            )
        )

        activity_input = ActivityModelInput(
            model_name=self.model_name,
            system_instructions=system_instructions,
            input=cast(Union[str, list[TResponseInputItem]], input),
            model_settings=model_settings,
            tools=tool_infos,
            output_schema=output_schema_input,
            handoffs=handoff_infos,
            tracing=ModelTracingInput.DISABLED,  # ModelTracingInput(tracing.value),
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
                self.activity_name, activity_input_json
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
