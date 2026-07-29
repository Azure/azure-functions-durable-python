# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Client operation correlation logging: `FunctionInvocationId` is now propagated via HTTP headers to the host for client operations, enabling correlation with host logs.
- Centralized JSON serialization module (`azure.durable_functions.models.utils.df_serialization`): all serialization/deserialization of user payloads (orchestrator inputs/outputs, activity arguments and results, sub-orchestrator payloads, entity inputs/outputs, and client inputs) now flows through `df_dumps` / `df_loads`, replacing scattered `json.dumps(…, default=_serialize_custom_object)` / `json.loads(…, object_hook=_deserialize_custom_object)` calls. This module is a thin shim over the Azure Functions SDK: when the installed `azure-functions` exposes `df_dumps` / `df_loads` (the centralized serializers with type-validation and strict-typing support), they are used directly so our serialization matches the SDK's `ActivityTriggerConverter` at the host boundary; otherwise it falls back to the legacy `_serialize_custom_object` / `_deserialize_custom_object` hooks, which keeps both sides symmetric. The wire format is **unchanged** — builtins serialize to plain JSON and custom objects continue to use the `{"__class__", "__module__", "__data__"}` convention.
- Type-hint-driven validation via `df_loads(s, expected_type=...)`: when the V2 programming model provides a return-type annotation for an activity or sub-orchestrator, the annotation is threaded through call sites so the SDK's `df_loads` can validate the deserialized payload against that type (when available). On older `azure-functions` releases the argument is accepted but ignored.
- Return-type discovery for V2 decorated activities/sub-orchestrators (`azure.durable_functions.models.utils.type_discovery`): resolves the concrete return annotation from the user's registered function, used to supply `expected_type` to `df_loads`.

### Fixed

- `purge_instance_history_by` now supplies the earliest supported creation time when `created_time_from` is omitted, avoiding HTTP 400 responses from the Durable extension.

## 1.0.0b6

- [Create timer](https://github.com/Azure/azure-functions-durable-python/issues/35) functionality available

## 1.0.0b5

- [Object serialization](https://github.com/Azure/azure-functions-durable-python/issues/90) made available
- [Can set custom status](https://github.com/Azure/azure-functions-durable-python/issues/117) of orchestration

## 1.0.0b3-b4
- Release to test CD pipeline with push to PyPI

## 1.0.0b2

### Fixed
- [Remove staticmethod definitions](https://github.com/Azure/azure-functions-durable-python/issues/65)

## 1.0.0b1

### Added

The following orchestration patterns are added:

- Function Chaining
- Fan In Fan Out
- Async HTTP APIs
- Human Interaction

#### API Parity
- CallActivity
- CallActivityWithRetry
- Task.all 
- Task.any 
- waitForExternalEvent
- continueAsNew
- callHttp
- currentUtcDateTime
- newUuid
- createCheckStatusResponse 
- getStatus
- getStatusAll
- getStatusBy
- purgeInstanceHistory
- purgeInstanceHistoryBy
- raiseEvent
- startNew
- terminate
- waitForCompletionOrCreateCheckStatusResponse

### Changed
N/A

### Fixed
N/A

### Removed
N/A
