#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import pytest
from unittest.mock import Mock, patch

from azure.durable_functions.openai_agents.context import DurableAIAgentContext
from azure.durable_functions.openai_agents.task_tracker import TaskTracker
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.models.RetryOptions import RetryOptions

from agents.tool import FunctionTool


class TestDurableAIAgentContext:
    """Test suite for DurableAIAgentContext class."""

    def _create_mock_orchestration_context(self):
        """Create a mock DurableOrchestrationContext for testing."""
        orchestration_context = Mock(spec=DurableOrchestrationContext)
        orchestration_context.call_activity = Mock(return_value="mock_task")
        orchestration_context.call_activity_with_retry = Mock(return_value="mock_task_with_retry")
        orchestration_context.instance_id = "test_instance_id"
        orchestration_context.current_utc_datetime = "2023-01-01T00:00:00Z"
        orchestration_context.is_replaying = False
        return orchestration_context

    def _create_mock_task_tracker(self):
        """Create a mock TaskTracker for testing."""
        task_tracker = Mock(spec=TaskTracker)
        task_tracker.record_activity_call = Mock()
        task_tracker.get_activity_call_result = Mock(return_value="activity_result")
        task_tracker.get_activity_call_result_with_retry = Mock(return_value="retry_activity_result")
        return task_tracker

    def _create_mock_activity_func(self, name="test_activity", input_name=None,
                                   activity_name=None):
        """Create a mock activity function with configurable parameters."""
        mock_activity_func = Mock()
        mock_activity_func._function._name = name
        mock_activity_func._function._func = lambda x: x

        if input_name is not None:
            # Create trigger with input_name
            mock_activity_func._function._trigger = Mock()
            mock_activity_func._function._trigger.activity = activity_name
            mock_activity_func._function._trigger.name = input_name
        else:
            # No trigger means no input_name
            mock_activity_func._function._trigger = None

        return mock_activity_func

    def _setup_activity_tool_mocks(self, mock_function_tool, mock_function_schema,
                                   activity_name="test_activity", description=""):
        """Setup common mocks for function_schema and FunctionTool."""
        mock_schema = Mock()
        mock_schema.name = activity_name
        mock_schema.description = description
        mock_schema.params_json_schema = {"type": "object"}
        mock_function_schema.return_value = mock_schema

        mock_tool = Mock(spec=FunctionTool)
        mock_function_tool.return_value = mock_tool

        return mock_tool

    def _invoke_activity_tool(self, run_activity, input_data):
        """Helper to invoke the activity tool with asyncio."""
        mock_ctx = Mock()
        import asyncio
        return asyncio.run(run_activity(mock_ctx, input_data))

    def _test_activity_tool_input_processing(self, input_name=None, input_data="",
                                           expected_input_parameter_value="",
                                           retry_options=None,
                                           activity_name="test_activity"):
        """Framework method that runs a complete input processing test."""
        with patch('azure.durable_functions.openai_agents.context.function_schema') \
             as mock_function_schema, \
             patch('azure.durable_functions.openai_agents.context.FunctionTool') \
             as mock_function_tool:

            # Setup
            orchestration_context = self._create_mock_orchestration_context()
            task_tracker = self._create_mock_task_tracker()
            mock_activity_func = self._create_mock_activity_func(
                name=activity_name, input_name=input_name)
            self._setup_activity_tool_mocks(
                mock_function_tool, mock_function_schema, activity_name)

            # Create context and tool
            ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)
            ai_context.create_activity_tool(mock_activity_func, retry_options=retry_options)

            # Get and invoke the run_activity function
            call_args = mock_function_tool.call_args
            run_activity = call_args[1]['on_invoke_tool']
            self._invoke_activity_tool(run_activity, input_data)

            # Verify the expected call was made
            if retry_options:
                task_tracker.get_activity_call_result_with_retry.assert_called_once_with(
                    activity_name, retry_options, expected_input_parameter_value
                )
            else:
                task_tracker.get_activity_call_result.assert_called_once_with(
                    activity_name, expected_input_parameter_value
                )

    def test_init_creates_context_successfully(self):
        """Test that __init__ creates a DurableAIAgentContext successfully."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()
        retry_options = RetryOptions(1000, 3)

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, retry_options)

        assert isinstance(ai_context, DurableAIAgentContext)
        assert not isinstance(ai_context, DurableOrchestrationContext)

    def test_call_activity_delegates_and_records(self):
        """Test that call_activity delegates to context and records activity call."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)
        result = ai_context.call_activity("test_activity", "test_input")

        orchestration_context.call_activity.assert_called_once_with("test_activity", "test_input")
        task_tracker.record_activity_call.assert_called_once()
        assert result == "mock_task"

    def test_call_activity_with_retry_delegates_and_records(self):
        """Test that call_activity_with_retry delegates to context and records activity call."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()
        retry_options = RetryOptions(1000, 3)

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)
        result = ai_context.call_activity_with_retry("test_activity", retry_options, "test_input")

        orchestration_context.call_activity_with_retry.assert_called_once_with(
            "test_activity", retry_options, "test_input"
        )
        task_tracker.record_activity_call.assert_called_once()
        assert result == "mock_task_with_retry"

    @patch('azure.durable_functions.openai_agents.context.function_schema')
    @patch('azure.durable_functions.openai_agents.context.FunctionTool')
    def test_activity_as_tool_creates_function_tool(self, mock_function_tool, mock_function_schema):
        """Test that create_activity_tool creates a FunctionTool with correct parameters."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        # Mock the activity function
        mock_activity_func = Mock()
        mock_activity_func._function._name = "test_activity"
        mock_activity_func._function._func = lambda x: x

        # Mock the schema
        mock_schema = Mock()
        mock_schema.name = "test_activity"
        mock_schema.description = "Test activity description"
        mock_schema.params_json_schema = {"type": "object"}
        mock_function_schema.return_value = mock_schema

        # Mock FunctionTool
        mock_tool = Mock(spec=FunctionTool)
        mock_function_tool.return_value = mock_tool

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)
        retry_options = RetryOptions(1000, 3)

        result = ai_context.create_activity_tool(
            mock_activity_func,
            description="Custom description",
            retry_options=retry_options
        )

        # Verify function_schema was called correctly
        mock_function_schema.assert_called_once_with(
            func=mock_activity_func._function._func,
            docstring_style=None,
            description_override="Custom description",
            use_docstring_info=True,
            strict_json_schema=True,
        )

        # Verify FunctionTool was created correctly
        mock_function_tool.assert_called_once()
        call_args = mock_function_tool.call_args
        assert call_args[1]['name'] == "test_activity"
        assert call_args[1]['description'] == "Test activity description"
        assert call_args[1]['params_json_schema'] == {"type": "object"}
        assert call_args[1]['strict_json_schema'] is True
        assert callable(call_args[1]['on_invoke_tool'])

        assert result is mock_tool

    @patch('azure.durable_functions.openai_agents.context.function_schema')
    @patch('azure.durable_functions.openai_agents.context.FunctionTool')
    def test_activity_as_tool_with_default_retry_options(self, mock_function_tool, mock_function_schema):
        """Test that create_activity_tool uses default retry options when none provided."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        mock_activity_func = Mock()
        mock_activity_func._function._name = "test_activity"
        mock_activity_func._function._func = lambda x: x

        mock_schema = Mock()
        mock_schema.name = "test_activity"
        mock_schema.description = "Test description"
        mock_schema.params_json_schema = {"type": "object"}
        mock_function_schema.return_value = mock_schema

        mock_tool = Mock(spec=FunctionTool)
        mock_function_tool.return_value = mock_tool

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)

        # Call with default retry options
        result = ai_context.create_activity_tool(mock_activity_func)

        # Should still create the tool successfully
        assert result is mock_tool
        mock_function_tool.assert_called_once()

    @patch('azure.durable_functions.openai_agents.context.function_schema')
    @patch('azure.durable_functions.openai_agents.context.FunctionTool')
    def test_activity_as_tool_run_activity_with_retry(self, mock_function_tool, mock_function_schema):
        """Test that the run_activity function calls task tracker with retry options."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        mock_activity_func = Mock()
        mock_activity_func._function._name = "test_activity"
        mock_activity_func._function._trigger = None
        mock_activity_func._function._func = lambda x: x

        mock_schema = Mock()
        mock_schema.name = "test_activity"
        mock_schema.description = ""
        mock_schema.params_json_schema = {"type": "object"}
        mock_function_schema.return_value = mock_schema

        mock_tool = Mock(spec=FunctionTool)
        mock_function_tool.return_value = mock_tool

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)
        retry_options = RetryOptions(1000, 3)

        ai_context.create_activity_tool(mock_activity_func, retry_options=retry_options)

        # Get the run_activity function that was passed to FunctionTool
        call_args = mock_function_tool.call_args
        run_activity = call_args[1]['on_invoke_tool']

        # Create a mock context wrapper
        mock_ctx = Mock()

        # Call the run_activity function
        import asyncio
        result = asyncio.run(run_activity(mock_ctx, "test_input"))

        # Verify the task tracker was called with retry options
        task_tracker.get_activity_call_result_with_retry.assert_called_once_with(
            "test_activity", retry_options, "test_input"
        )
        assert result == "retry_activity_result"

    @patch('azure.durable_functions.openai_agents.context.function_schema')
    @patch('azure.durable_functions.openai_agents.context.FunctionTool')
    def test_activity_as_tool_run_activity_without_retry(self, mock_function_tool, mock_function_schema):
        """Test that the run_activity function calls task tracker without retry when retry_options is None."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        mock_activity_func = Mock()
        mock_activity_func._function._name = "test_activity"
        mock_activity_func._function._trigger = None
        mock_activity_func._function._func = lambda x: x

        mock_schema = Mock()
        mock_schema.name = "test_activity"
        mock_schema.description = ""
        mock_schema.params_json_schema = {"type": "object"}
        mock_function_schema.return_value = mock_schema

        mock_tool = Mock(spec=FunctionTool)
        mock_function_tool.return_value = mock_tool

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)

        ai_context.create_activity_tool(mock_activity_func, retry_options=None)

        # Get the run_activity function that was passed to FunctionTool
        call_args = mock_function_tool.call_args
        run_activity = call_args[1]['on_invoke_tool']

        # Create a mock context wrapper
        mock_ctx = Mock()

        # Call the run_activity function
        import asyncio
        result = asyncio.run(run_activity(mock_ctx, "test_input"))

        # Verify the task tracker was called without retry options
        task_tracker.get_activity_call_result.assert_called_once_with(
            "test_activity", "test_input"
        )
        assert result == "activity_result"

    @patch('azure.durable_functions.openai_agents.context.function_schema')
    @patch('azure.durable_functions.openai_agents.context.FunctionTool')
    def test_activity_as_tool_extracts_activity_name_from_trigger(self, mock_function_tool, mock_function_schema):
        """Test that the run_activity function calls task tracker with the activity name specified in the trigger."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        mock_activity_func = Mock()
        mock_activity_func._function._name = "test_activity"
        mock_activity_func._function._trigger.activity = "activity_name_from_trigger"
        mock_activity_func._function._func = lambda x: x

        mock_schema = Mock()
        mock_schema.name = "test_activity"
        mock_schema.description = ""
        mock_schema.params_json_schema = {"type": "object"}
        mock_function_schema.return_value = mock_schema

        mock_tool = Mock(spec=FunctionTool)
        mock_function_tool.return_value = mock_tool

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)

        ai_context.create_activity_tool(mock_activity_func, retry_options=None)

        # Get the run_activity function that was passed to FunctionTool
        call_args = mock_function_tool.call_args
        run_activity = call_args[1]['on_invoke_tool']

        # Create a mock context wrapper
        mock_ctx = Mock()

        # Call the run_activity function
        import asyncio
        result = asyncio.run(run_activity(mock_ctx, "test_input"))

        # Verify the task tracker was called without retry options
        task_tracker.get_activity_call_result.assert_called_once_with(
            "activity_name_from_trigger", "test_input"
        )
        assert result == "activity_result"

    def test_create_activity_tool_parses_json_input_with_input_name(self):
        """Test JSON input parsing and named value extraction with input_name."""
        self._test_activity_tool_input_processing(
            input_name="max",
            input_data='{"max": 100}',
            expected_input_parameter_value=100,
            activity_name="random_number_tool"
        )

    def test_create_activity_tool_handles_non_json_input_gracefully(self):
        """Test non-JSON input passes through unchanged with input_name."""
        self._test_activity_tool_input_processing(
            input_name="param",
            input_data="not json",
            expected_input_parameter_value="not json"
        )

    def test_create_activity_tool_handles_json_missing_named_parameter(self):
        """Test JSON input without named parameter passes through unchanged."""
        json_input = '{"other_param": 200}'
        self._test_activity_tool_input_processing(
            input_name="expected_param",
            input_data=json_input,
            expected_input_parameter_value=json_input
        )

    def test_create_activity_tool_handles_malformed_json_gracefully(self):
        """Test malformed JSON passes through unchanged."""
        malformed_json = '{"param": 100'  # Missing closing brace
        self._test_activity_tool_input_processing(
            input_name="param",
            input_data=malformed_json,
            expected_input_parameter_value=malformed_json
        )

    def test_create_activity_tool_json_parsing_works_with_retry_options(self):
        """Test JSON parsing works correctly with retry options."""
        retry_options = RetryOptions(1000, 3)
        self._test_activity_tool_input_processing(
            input_name="value",
            input_data='{"value": "test_data"}',
            expected_input_parameter_value="test_data",
            retry_options=retry_options
        )

    def test_create_activity_tool_no_input_name_passes_through_json(self):
        """Test JSON input passes through unchanged when no input_name."""
        json_input = '{"param": 100}'
        self._test_activity_tool_input_processing(
            input_name=None,  # No input_name
            input_data=json_input,
            expected_input_parameter_value=json_input
        )

    def test_context_delegation_methods_work(self):
        """Test that common context methods work through delegation."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        # Add some mock methods to the orchestration context
        orchestration_context.wait_for_external_event = Mock(return_value="external_event_task")
        orchestration_context.create_timer = Mock(return_value="timer_task")

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)

        # These should work through delegation
        result1 = ai_context.wait_for_external_event("test_event")
        result2 = ai_context.create_timer("2023-01-01T00:00:00Z")

        assert result1 == "external_event_task"
        assert result2 == "timer_task"
        orchestration_context.wait_for_external_event.assert_called_once_with("test_event")
        orchestration_context.create_timer.assert_called_once_with("2023-01-01T00:00:00Z")

    def test_getattr_delegates_to_context(self):
        """Test that __getattr__ delegates attribute access to the underlying context."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)

        # Test delegation of various attributes
        assert ai_context.instance_id == "test_instance_id"
        assert ai_context.current_utc_datetime == "2023-01-01T00:00:00Z"
        assert ai_context.is_replaying is False

    def test_getattr_raises_attribute_error_for_nonexistent_attributes(self):
        """Test that __getattr__ raises AttributeError for non-existent attributes."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)

        with pytest.raises(AttributeError, match="'DurableAIAgentContext' object has no attribute 'nonexistent_attr'"):
            _ = ai_context.nonexistent_attr

    def test_dir_includes_delegated_attributes(self):
        """Test that __dir__ includes attributes from the underlying context."""
        orchestration_context = self._create_mock_orchestration_context()
        task_tracker = self._create_mock_task_tracker()

        ai_context = DurableAIAgentContext(orchestration_context, task_tracker, None)
        dir_result = dir(ai_context)

        # Should include delegated attributes from the underlying context
        assert 'instance_id' in dir_result
        assert 'current_utc_datetime' in dir_result
        assert 'is_replaying' in dir_result
        # Should also include public methods
        assert 'call_activity' in dir_result
        assert 'create_activity_tool' in dir_result
