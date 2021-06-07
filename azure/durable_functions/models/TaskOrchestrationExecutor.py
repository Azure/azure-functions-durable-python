from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.models.MutableTask import MutableTask
from typing import List
from azure.durable_functions.models.history.HistoryEventType import HistoryEventType
from azure.durable_functions.models.history.HistoryEvent import HistoryEvent


class TaskOrchestrationExecutor:

    def __init__(self):
        self.current_task = MutableTask(-1)
        self.current_task.set_result(None)

        self.is_done = False
        self.output = None
        self.exception = None

    def execute(self, context: DurableOrchestrationContext, history: List[HistoryEvent], generator) -> str:
        self.context = context
        self.generator = generator(context) # TODO: handle non-yield fn case
        for event in history:
            context._is_replaying = event.is_played
            self.process_event(event)
            if self._is_done_executing():
                break
        return self.gen_orchestrator_state()

    def process_event(self, event: HistoryEvent):
        event_type = event.event_type
        if event_type == HistoryEventType.ORCHESTRATOR_STARTED:
            return
        if event_type == HistoryEventType.ORCHESTRATOR_COMPLETED:
            return
        elif event_type == HistoryEventType.EXECUTION_STARTED:
            self.context.current_utc_datetime = event.timestamp
            self.resume()
        elif event_type == HistoryEventType.TASK_SCHEDULED:
            return
        elif event_type == HistoryEventType.TASK_COMPLETED:
            key = event.TaskScheduledId
            activity_task = self.context.open_tasks[key]
            self.context.open_tasks.pop(key)

            activity_task.set_result("TBD")
            self.resume()
        elif event.event_type == HistoryEventType.TIMER_CREATED:
            raise NotImplementedError
        elif event.event_type == HistoryEventType.TIMER_FIRED:
            raise NotImplementedError
        else:
            raise NotImplementedError
    
    def resume(self):
        current_task = self.current_task
        if current_task.is_completed:
            task = self.step(current_task.result)
        self.current_task = task
    
    def step(self, task_result):
        task = None
        try:
            task = self.generator.send(task_result)
        except StopIteration as stop_exception:
            self.is_done = True
            self.output = stop_exception.value
        except Exception as exception:
            self.exception = exception
        return task
    
    def gen_orchestrator_state(self) -> str:
        state = OrchestratorState(
            is_done=self.is_done,
            actions=self.context.actions,
            output=self.output,
            error=str(self.exception) if isinstance(self.exception, Exception) else None,
            custom_status=self.context.custom_status
        )

        if self.exception is not None:
            # Create formatted error, using out-of-proc error schema
            error_label = "\n\n$OutOfProcData$:"
            state_str = state.to_json_string()
            formatted_error = f"{self.exception}{error_label}{state_str}"

            # Raise exception, re-set stack to original location
            raise Exception(formatted_error) from self.exception
        return state.to_json_string()
    
    def _is_done_executing(self) -> bool:
        return self.is_done or isinstance(self.exception, Exception)
