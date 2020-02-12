# API Implementation Status

Documents the capability exposed by JavaScript durable functions and the status of implementation within Python

| Class Exposed On	| Method	| In Python?	| Documentation |
| :---------------- | :-------- | :------------ | :------------ |
| Orchestrator | CallActivity | yes | Schedules an activity function named `name` for execution.
| Orchestrator | CallActivityWithRetry	| yes | Schedules an activity function named `name` for execution with retry options.
| Orchestrator | all | yes | Similar to Promise.all. When called with `yield` or `return`, returns an array containing the results of all [[Task]]s passed to it. It returns when all of the [[Task]] instances have completed.
| Orchestrator | any | yes | Similar to Promise.race. When called with `yield` or `return`, returns the first [[Task]] instance to complete.
| Orchestrator | waitForExternalEvent	| yes | Waits asynchronously for an event to be raised with the name `name` and returns the event data.
| Orchestrator | continueAsNew	| no | Restarts the orchestration by clearing its history.
| Orchestrator | callEntity | no | Calls an operation on an entity, passing an argument, and waits for it to complete.
| Orchestrator | callSubOrchestrator| no |Schedules an orchestration function named `name` for execution.
| Orchestrator | callSubOrchestratorWithRetry |	no | Schedules an orchestrator function named `name` for execution with retry options.
| Orchestrator | callHttp | no | Schedules a durable HTTP call to the specified endpoint.
| Orchestrator | createTimer | yes | Creates a durable timer that expires at a specified time.
| Orchestrator | getInput | yes | Gets the input of the current orchestrator function as a deserialized value.
| Orchestrator | setCustomStatus | no | Sets the JSON-serializable status of the current orchestrator function.
| Orchestrator | currentUtcDateTime | yes | Gets the current date/time in a way that is safe for use by orchestrator functions.
| Orchestrator | newGuid | no | Creates a new GUID that is safe for replay within an orchestration or operation.
| client | createCheckStatusResponse | yes| Creates an HTTP response that is useful for checking the status of the specified instance.
| client | createHttpManagementPayload | no | Creates an [[HttpManagementPayload]] object that contains instance management HTTP endpoints.
| client | getStatus | no | Gets the status of the specified orchestration instance.
| client | getStatusAll | no | Gets the status of all orchestration instances. 
| client | getStatusBy | no | Gets the status of all orchestration instances that match the specified conditions.
| client | purgeInstanceHistory | no | Purge the history for a concrete instance.
| client | purgeInstanceHistoryBy | no | Purge the orchestration history for instances that match the conditions.
| client | raiseEvent | yes | Sends an event notification message to a waiting orchestration instance.
| client | readEntityState | no | Tries to read the current state of an entity. Returns undefined if the entity does not exist, or if the JSON-serialized state of the entity is larger than 16KB.
| client | rewind | no | Rewinds the specified failed orchestration instance with a reason.
| client | signalEntity | no | Signals an entity to perform an operation.
| client | startNew | yes | Starts a new instance of the specified orchestrator function.
| client | terminate | no | Terminates a running orchestration instance.
| client | waitForCompletionOrCreateCheckStatusResponse | no | Creates an HTTP response which either contains a payload of management URLs for a non-completed instance or contains the payload containing the output of the completed orchestration.
| ManagedIdentityTokenSource| | no | Returns a `ManagedIdentityTokenSource` object.
 