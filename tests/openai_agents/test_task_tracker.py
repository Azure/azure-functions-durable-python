#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import pytest
import json
from unittest.mock import Mock

from azure.durable_functions.openai_agents.task_tracker import TaskTracker
from azure.durable_functions.openai_agents.exceptions import YieldException
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from azure.durable_functions.models.history.HistoryEventType import HistoryEventType
from azure.durable_functions.models.RetryOptions import RetryOptions


class MockTask:
    """Mock Task object for testing."""

    def __init__(self, activity_name: str, input_data: str):
        self.activity_name = activity_name
        self.input = input_data
        self.id = f"task_{activity_name}"


def create_mock_context(task_completed_results=None):
    """Create a mock DurableOrchestrationContext with configurable history.

    Args:
    ----
        task_completed_results: List of objects to be serialized as JSON results.
                               Each object will be json.dumps() serialized automatically.
    """
    context = Mock(spec=DurableOrchestrationContext)

    # Create history events for completed tasks
    histories = []
    if task_completed_results:
        for i, result_object in enumerate(task_completed_results):
            history_event = Mock(spec=HistoryEvent)
            history_event.event_type = HistoryEventType.TASK_COMPLETED
            history_event.Result = json.dumps(result_object)
            histories.append(history_event)

    context.histories = histories

    # Mock call_activity method
    def mock_call_activity(activity_name, input_data):
        return MockTask(activity_name, input_data)

    context.call_activity = Mock(side_effect=mock_call_activity)

    # Mock call_activity_with_retry method
    def mock_call_activity_with_retry(activity_name, retry_options, input_data):
        return MockTask(activity_name, input_data)

    context.call_activity_with_retry = Mock(side_effect=mock_call_activity_with_retry)

    return context


class TestTaskTracker:
    """Tests for the TaskTracker implementation."""

    def _consume_generator_with_return_value(self, generator):
        """Consume a generator and capture both yielded items and return value.

        Returns
        -------
        tuple
            (yielded_items, return_value) where return_value is None if no return value
        """
        yielded_items = []
        return_value = None
        try:
            while True:
                yielded_items.append(next(generator))
        except StopIteration as e:
            return_value = e.value
        return yielded_items, return_value

    def test_get_activity_call_result_returns_result_when_history_available(self):
        """Test get_activity_call_result returns result when history is available."""
        context = create_mock_context(task_completed_results=["test_result"])
        tracker = TaskTracker(context)

        result = tracker.get_activity_call_result("test_activity", "test_input")
        assert result == "test_result"

    def test_get_activity_call_result_raises_yield_exception_when_no_history(self):
        """Test get_activity_call_result raises YieldException when no history."""
        context = create_mock_context(task_completed_results=[])
        tracker = TaskTracker(context)

        with pytest.raises(YieldException) as exc_info:
            tracker.get_activity_call_result("test_activity", "test_input")

        task = exc_info.value.task
        assert task.activity_name == "test_activity"
        assert task.input == "test_input"

    def test_get_activity_call_result_with_retry_returns_result_when_history_available(self):
        """Test get_activity_call_result_with_retry returns result when history is available."""
        context = create_mock_context(task_completed_results=["result"])
        tracker = TaskTracker(context)
        retry_options = RetryOptions(1000, 3)

        result = tracker.get_activity_call_result_with_retry("activity", retry_options, "input")
        assert result == "result"

    def test_get_activity_call_result_with_retry_raises_yield_exception_when_no_history(self):
        """Test get_activity_call_result_with_retry raises YieldException when no history."""
        context = create_mock_context(task_completed_results=[])
        tracker = TaskTracker(context)
        retry_options = RetryOptions(1000, 3)

        with pytest.raises(YieldException) as exc_info:
            tracker.get_activity_call_result_with_retry("activity", retry_options, "input")

        task = exc_info.value.task
        assert task.activity_name == "activity"
        assert task.input == "input"

    def test_multiple_activity_calls_with_partial_history(self):
        """Test sequential activity calls with partial history available."""
        context = create_mock_context(task_completed_results=["result1", "result2"])
        tracker = TaskTracker(context)

        # First call returns result1
        result1 = tracker.get_activity_call_result("activity1", "input1")
        assert result1 == "result1"

        # Second call returns result2
        result2 = tracker.get_activity_call_result("activity2", "input2")
        assert result2 == "result2"

        # Third call raises YieldException (no more history)
        with pytest.raises(YieldException):
            tracker.get_activity_call_result("activity3", "input3")

    def test_execute_orchestrator_function_return_value(self):
        """Test execute_orchestrator_function with orchestrator function that returns a value."""
        context = create_mock_context()
        tracker = TaskTracker(context)

        expected_result = "orchestrator_result"

        def test_orchestrator():
            return expected_result

        result_gen = tracker.execute_orchestrator_function(test_orchestrator)
        yielded_items, return_value = self._consume_generator_with_return_value(result_gen)

        # Should yield nothing and return the value
        assert yielded_items == []
        assert return_value == expected_result

    def test_execute_orchestrator_function_get_activity_call_result_incomplete(self):
        """Test execute_orchestrator_function with orchestrator function that tries to get an activity result before this activity call completes (not a replay)."""
        context = create_mock_context()  # No history available
        tracker = TaskTracker(context)

        def test_orchestrator():
            return tracker.get_activity_call_result("activity", "test_input")

        result_gen = tracker.execute_orchestrator_function(test_orchestrator)
        yielded_items, return_value = self._consume_generator_with_return_value(result_gen)

        # Should yield a task with this activity name
        assert yielded_items[0].activity_name == "activity"
        assert len(yielded_items) == 1
        assert return_value is None

    def test_execute_orchestrator_function_get_complete_activity_result(self):
        """Test execute_orchestrator_function with orchestrator function that gets a complete activity call result (replay)."""
        context = create_mock_context(task_completed_results=["activity_result"])
        tracker = TaskTracker(context)

        def test_orchestrator():
            return tracker.get_activity_call_result("activity", "test_input")

        result_gen = tracker.execute_orchestrator_function(test_orchestrator)
        yielded_items, return_value = self._consume_generator_with_return_value(result_gen)

        # Should yield the queued task and return the result
        assert yielded_items[0].activity_name == "activity"
        assert len(yielded_items) == 1
        assert return_value == "activity_result"

    def test_execute_orchestrator_function_yields_tasks(self):
        """Test execute_orchestrator_function with orchestrator function that yields tasks."""
        context = create_mock_context()
        tracker = TaskTracker(context)

        def test_orchestrator():
            yield "task_1"
            yield "task_2"
            return "final_result"

        result_gen = tracker.execute_orchestrator_function(test_orchestrator)
        yielded_items, return_value = self._consume_generator_with_return_value(result_gen)

        # Should yield the tasks in order and return the final result
        assert yielded_items[0] == "task_1"
        assert yielded_items[1] == "task_2"
        assert len(yielded_items) == 2
        assert return_value == "final_result"

    def test_execute_orchestrator_function_context_activity_call_incomplete(self):
        """Test execute_orchestrator_function with orchestrator function that tries to get an activity result before this activity call completes (not a replay) after a DurableAIAgentContext.call_activity invocation."""
        context = create_mock_context(task_completed_results=["result1"])
        tracker = TaskTracker(context)

        def test_orchestrator():
            # Simulate invoking DurableAIAgentContext.call_activity and yielding the resulting task
            tracker.record_activity_call()
            yield "task" # Produced "result1"

            return tracker.get_activity_call_result("activity", "input") # Incomplete, should raise YieldException that will be translated to yield

        result_gen = tracker.execute_orchestrator_function(test_orchestrator)
        yielded_items, return_value = self._consume_generator_with_return_value(result_gen)

        # Should yield the incomplete task
        assert yielded_items[0] == "task"
        assert yielded_items[1].activity_name == "activity"
        assert len(yielded_items) == 2
        assert return_value == None

    def test_execute_orchestrator_function_context_activity_call_complete(self):
        """Test execute_orchestrator_function with orchestrator function that gets a complete activity call result (replay) after a DurableAIAgentContext.call_activity invocation."""
        context = create_mock_context(task_completed_results=["result1", "result2"])
        tracker = TaskTracker(context)

        def test_orchestrator():
            # Simulate invoking DurableAIAgentContext.call_activity and yielding the resulting task
            tracker.record_activity_call()
            yield "task" # Produced "result1"

            return tracker.get_activity_call_result("activity", "input") # Complete, should return "result2"

        result_gen = tracker.execute_orchestrator_function(test_orchestrator)
        yielded_items, return_value = self._consume_generator_with_return_value(result_gen)

        # Should yield the queued task and return the result
        assert yielded_items[0] == "task"
        assert yielded_items[1].activity_name == "activity"
        assert len(yielded_items) == 2
        assert return_value == "result2"

    def test_execute_orchestrator_function_mixed_behaviors_combination(self):
        """Test execute_orchestrator_function mixing all documented behaviors."""
        context = create_mock_context(task_completed_results=[
            "result1",
            "result2",
            "result3",
            "result4"
        ])
        tracker = TaskTracker(context)

        def test_orchestrator():
            activity1_result = tracker.get_activity_call_result("activity1", "input1")

            # Simulate invoking DurableAIAgentContext.call_activity("activity2") and yielding the resulting task
            tracker.record_activity_call()
            yield "yielded task from activity2" # Produced "result2"
            
            # Yield a regular task, possibly returned from DurableAIAgentContext methods like wait_for_external_event, etc.
            yield "another yielded task"
            
            activity3_result = tracker.get_activity_call_result("activity3", "input3")

            # Simulate invoking DurableAIAgentContext.call_activity("activity4") and yielding the resulting task
            tracker.record_activity_call()
            yield "yielded task from activity4" # Produced "result4"

            return f"activity1={activity1_result};activity3={activity3_result}"

        result_gen = tracker.execute_orchestrator_function(test_orchestrator)
        yielded_items, return_value = self._consume_generator_with_return_value(result_gen)

        # Verify yield order
        assert yielded_items[0].activity_name == "activity1"
        assert yielded_items[1] == "yielded task from activity2"
        assert yielded_items[2] == "another yielded task"
        assert yielded_items[3].activity_name == "activity3"
        assert yielded_items[4] == "yielded task from activity4"
        assert len(yielded_items) == 5

        # Verify return value
        expected_return = "activity1=result1;activity3=result3"
        assert return_value == expected_return
