from azure.durable_functions.models.NewTask import TaskState
from azure.durable_functions.tasks.task_utilities import parse_history_event
from azure.durable_functions.models.OrchestratorState import OrchestratorState
from azure.durable_functions.models.DurableOrchestrationContext import DurableOrchestrationContext
from azure.durable_functions.models.MutableTask import MutableTask
from typing import List
from azure.durable_functions.models.history.HistoryEventType import HistoryEventType
from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from types import GeneratorType

class TaskOrchestrationExecutor:

    def __init__(self):
        self.initialize()
    
    def initialize(self):
        self.current_task = MutableTask(-1, [])
        self.current_task.handle_result(None)

        self.orchestrator_returned = False
        self.output = None
        self.exception = None

    def execute(self, context: DurableOrchestrationContext, history: List[HistoryEvent], fn) -> str:
        self.context = context
        evaluated_user_code = fn(context)

        if isinstance(evaluated_user_code, GeneratorType):
            self.generator = evaluated_user_code
            for event in history:
                context._is_replaying = event.is_played
                self.process_event(event)
                if self._is_done_executing():
                    break
        elif not self.context._continue_as_new_flag:
            self.orchestrator_returned = True
            self.output = evaluated_user_code
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
            self.f(event, "TaskScheduledId", "Result")
        elif event_type == HistoryEventType.TASK_FAILED:
            self.f2(event, "TaskScheduledId")
        elif event.event_type == HistoryEventType.TIMER_CREATED:
            return
        elif event.event_type == HistoryEventType.TIMER_FIRED:
            # similar to the activity completion block
            self.f(event, "TimerId", "TimerId")
        elif event.event_type == HistoryEventType.SUB_ORCHESTRATION_INSTANCE_CREATED:
            return
        elif event.event_type == HistoryEventType.SUB_ORCHESTRATION_INSTANCE_COMPLETED:
            self.f(event, "TaskScheduledId", "Result")
        elif event.event_type == HistoryEventType.SUB_ORCHESTRATION_INSTANCE_FAILED:
            self.f2(event, "TaskScheduledId")
        elif event.event_type == HistoryEventType.EVENT_SENT:
            return
        elif event.event_type == HistoryEventType.EVENT_RAISED:
            self.f(event, "Name", "Input")
        elif event.event_type == HistoryEventType.CONTINUE_AS_NEW:
            self.initialize()
        else:
            raise NotImplementedError

    def f(self, event, key_attribute, result_attribute):
        key = getattr(event, key_attribute, None)
        if key is None:
            raise Exception("TBD")
        task = self.context.open_tasks[key]
        self.context.open_tasks.pop(key)

        result = getattr(event, result_attribute, None)
        if result is None:
            raise Exception("TBD")
        result = parse_history_event(event)
        task.handle_result(result)
        self.resume()

    def f2(self, event, key_attribute):
        key = getattr(event, key_attribute, None)
        if key is None:
            raise Exception("TBD")
        task = self.context.open_tasks[key]
        self.context.open_tasks.pop(key)

        exception = Exception(f"{event.Reason} \n {event.Details}")
        task.handle_error(exception)
        self.resume()
    
    def resume(self):
        current_task = self.current_task
        if not (current_task.state is TaskState.RUNNING):
            task = self.step(current_task)
            if not(task is None):
                if not(task.was_yielded):
                    task.was_yielded = True
                    self.current_task = task
                    self.context._add_to_actions(task.actions)

                else:
                    # TODO: test, but I think this means that we yielded a completed task?
                    self.resume()
  
    def step(self, task):
        new_task = None
        try:
            if task.state is TaskState.FAILED:
                new_task = self.generator.throw(task.error)
            else:
                new_task = self.generator.send(task.result)
        except StopIteration as stop_exception:
            self.orchestrator_returned = True
            self.output = stop_exception.value
        except Exception as exception:
            self.exception = exception
        return new_task
    
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

    @property
    def is_done(self):
        return self.orchestrator_returned or self.context.will_continue_as_new
