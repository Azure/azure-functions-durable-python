import logging
import json
import traceback
from typing import Callable, Iterator, List, Any, Union, Dict
from datetime import datetime
from dateutil.parser import parse as dtparse
from .interfaces import IFunctionContext, IAction
from .models.actions import CallActivityAction
from .models.history import HistoryEvent, HistoryEventType
from .models import (
    DurableOrchestrationContext,
    Task,
    TaskSet,
    OrchestratorState)


class Orchestrator:
    def __init__(self,
                 activity_func: Callable[[IFunctionContext], Iterator[Any]]):
        self.fn: Callable[[IFunctionContext], Iterator[Any]] = activity_func
        self.currentUtcDateTime: datetime = None
        self.customStatus: Any = None
        self.newGuidCounter: int = 0

    def handle(self, context_string: str):
        context: Dict[str, Any] = json.loads(context_string)
        logging.warn(f"!!!Calling orchestrator handle {context}")
        context_histories: List[HistoryEvent] = context.get("history")
        context_input = context.get("input")
        context_instanceId = context.get("instanceId")
        context_isReplaying = context.get("isReplaying")
        context_parentInstanceId = context.get("parentInstanceId")

        decisionStartedEvent: HistoryEvent = list(filter(
            # HistoryEventType.OrchestratorStarted
            lambda e: e["EventType"] == HistoryEventType.OrchestratorStarted,
            context_histories))[0]

        self.currentUtcDateTime = dtparse(decisionStartedEvent["Timestamp"])
        self.newGuidCounter = 0

        durable_context = DurableOrchestrationContext(
            instanceId=context_instanceId,
            isReplaying=context_isReplaying,
            parentInstanceId=context_parentInstanceId,
            callActivity=lambda n, i: self.callActivity(
                state=context_histories,
                name=n,
                input=i),
            task_all=lambda t: self.task_all(state=context_histories, tasks=t),
            currentUtcDateTime=self.currentUtcDateTime)
        activity_context = IFunctionContext(df=durable_context)

        gen = self.fn(activity_context)
        actions: List[List[IAction]] = []
        partialResult: Union[Task, TaskSet] = None

        try:
            if partialResult is not None:
                gen_result = gen.send(partialResult.result)
            else:
                gen_result = gen.send(None)

            while True:
                logging.warn(f"!!!actions {actions}")
                logging.warn(f"!!!Generator Execution {gen_result}")

                partialResult = gen_result

                if (isinstance(partialResult, Task)
                   and hasattr(partialResult, "action")):
                    actions.append([partialResult.action])
                elif (isinstance(partialResult, TaskSet)
                      and hasattr(partialResult, "actions")):
                    actions.append(partialResult.actions)

                if self.shouldSuspend(partialResult):
                    logging.warn(f"!!!Generator Suspended")
                    response = OrchestratorState(
                        isDone=False,
                        output=None,
                        actions=actions,
                        customStatus=self.customStatus)
                    return response.to_json_string()

                if (isinstance(partialResult, Task)
                   or isinstance(partialResult, TaskSet)) and (
                       partialResult.isFaulted):
                    gen.throw(partialResult.exception)
                    continue

                lastTimestamp = dtparse(decisionStartedEvent["Timestamp"])
                decisionStartedEvents = list(
                    filter(lambda e: (
                        e["EventType"] == HistoryEventType.OrchestratorStarted
                        and dtparse(e["Timestamp"]) > lastTimestamp),
                        context_histories))

                if len(decisionStartedEvents) == 0:
                    activity_context.df.currentUtcDateTime = None
                    self.currentTimestamp = None
                else:
                    decisionStartedEvent = decisionStartedEvents[0]
                    newTimestamp = dtparse(decisionStartedEvent["Timestamp"])
                    activity_context.df.currentUtcDateTime = newTimestamp
                    self.currentTimestamp = newTimestamp

                logging.warn(f"!!!Generator Execution {gen_result}")
                if partialResult is not None:
                    gen_result = gen.send(partialResult.result)
                else:
                    gen_result = gen.send(None)
        except StopIteration as sie:
            logging.warn(f"!!!Generator Termination StopIteration {sie}")
            response = OrchestratorState(
                isDone=True,
                output=sie.value,
                actions=actions,
                customStatus=self.customStatus)
            return response.to_json_string()
        except Exception as e:
            e_string = traceback.format_exc()
            logging.warn(f"!!!Generator Termination Exception {e_string}")
            response = OrchestratorState(
                isDone=False,
                output=None,  # Should have no output, after generation range
                actions=actions,
                error=str(e),
                customStatus=self.customStatus)
            return response.to_json_string()

    def callActivity(self,
                     state: List[HistoryEvent],
                     name: str,
                     input: Any = None) -> Task:
        logging.warn(f"!!!callActivity name={name} input={input}")
        newAction = CallActivityAction(name, input)

        taskScheduled = self.findTaskScheduled(state, name)
        taskCompleted = self.findTaskCompleted(state, taskScheduled)
        taskFailed = self.findTaskFailed(state, taskScheduled)
        self.setProcessed([taskScheduled, taskCompleted, taskFailed])

        if taskCompleted is not None:
            logging.warn("!!!Task Completed")
            return Task(
                isCompleted=True,
                isFaulted=False,
                action=newAction,
                result=self.parseHistoryEvent(taskCompleted),
                timestamp=taskCompleted["Timestamp"],
                id=taskCompleted["TaskScheduledId"])

        if taskFailed is not None:
            logging.warn("!!!Task Failed")
            return Task(
                isCompleted=True,
                isFaulted=True,
                action=newAction,
                result=taskFailed["Reason"],
                timestamp=taskFailed["Timestamp"],
                id=taskFailed["TaskScheduledId"],
                exc=Exception(f"TaskFailed {taskFailed['TaskScheduledId']}")
            )

        return Task(isCompleted=False, isFaulted=False, action=newAction)

    def task_all(self, state, tasks):
        allActions = []
        results = []
        isCompleted = True
        for task in tasks:
            allActions.append(task.action)
            results.append(task.result)
            if not task.isCompleted:
                isCompleted = False

        if isCompleted:
            return TaskSet(isCompleted, allActions, results)
        else:
            return TaskSet(isCompleted, allActions, None)

    def findTaskScheduled(self, state, name):
        if not name:
            raise ValueError("Name cannot be empty")

        tasks = list(
            filter(lambda e: e["EventType"] == HistoryEventType.TaskScheduled
                   and e["Name"] == name
                   and not e.get("IsProcessed"), state))

        logging.warn(f"!!! findTaskScheduled {tasks}")
        if len(tasks) == 0:
            return None

        return tasks[0]

    def findTaskCompleted(self, state, scheduledTask):
        if scheduledTask is None:
            return None

        tasks = list(
            filter(lambda e: e["EventType"] == HistoryEventType.TaskCompleted
                   and e.get("TaskScheduledId") == scheduledTask["EventId"],
                   state))

        if len(tasks) == 0:
            return None

        return tasks[0]

    def findTaskFailed(self, state, scheduledTask):
        if scheduledTask is None:
            return None

        tasks = list(
            filter(lambda e: e["EventType"] == HistoryEventType.TaskFailed
                   and e.get("TaskScheduledId") == scheduledTask["EventId"],
                   state))

        if len(tasks) == 0:
            return None

        return tasks[0]

    def setProcessed(self, tasks):
        for task in tasks:
            if task is not None:
                logging.warn(f"!!!task {task.get('IsProcessed')}"
                             f"{task.get('Name')}")
                task["IsProcessed"] = True
                logging.warn(f"!!!aftertask {task.get('IsProcessed')}"
                             f"{task.get('Name')}")

    def parseHistoryEvent(self, directiveResult):
        eventType = directiveResult.get("EventType")
        if eventType is None:
            raise ValueError("EventType is not found in task object")

        if eventType == HistoryEventType.EventRaised:
            return directiveResult["Input"]
        if eventType == HistoryEventType.SubOrchestrationInstanceCreated:
            return directiveResult["Result"]
        if eventType == HistoryEventType.TaskCompleted:
            return directiveResult["Result"]
        return None

    def shouldSuspend(self, partialResult) -> bool:  # old_name: shouldFinish
        logging.warn("!!!shouldSuspend")
        return bool(partialResult is not None
                    and hasattr(partialResult, "isCompleted")
                    and not partialResult.isCompleted)

    @classmethod
    def create(cls, fn):
        logging.warn("!!!Calling orchestrator create")
        return lambda context: Orchestrator(fn).handle(context)
