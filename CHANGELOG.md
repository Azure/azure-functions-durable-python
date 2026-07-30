# Changelog

All notable changes to this project are documented in this file. Release dates
and yanked-release status are based on the
[azure-functions-durable package on PyPI](https://pypi.org/project/azure-functions-durable/#history).

## Unreleased

## 1.7.0 - 2026-07-30

### Added

- Added `instance_id_prefix` filtering to
  `DurableOrchestrationClient.get_status_by`.
- Added `DurableFunctionsCompatibilityWarning`, emitted at import time for
  applications using the legacy `function.json` programming model unless
  `requirements.txt` demonstrably restricts `azure-functions-durable` below
  version 2.

### Changed

- `purge_instance_history_by` now raises a clear `ValueError` when the required
  `created_time_from` argument is omitted, instead of sending a request that
  the Durable extension rejects.

### Fixed

- Fixed `durableClient` binding validation on Python 3.14.

## 1.6.0 - 2026-07-09

### Added

- Added `restart` support to `DurableOrchestrationClient`.
- Centralized serialization and deserialization of user payloads through
  `df_dumps` and `df_loads`. When the installed `azure-functions` SDK exposes
  these APIs, Durable Functions uses its type-validating codec; older SDK
  versions retain the legacy fallback. The wire format remains unchanged.
- Added type-hint-driven validation for activity and sub-orchestrator results
  by passing their expected return types to `df_loads`.
- Added return-type discovery for activities and sub-orchestrators registered
  with Python v2 programming model decorators.
- Added Python 3.13 and 3.14 support.

### Changed

- `is_replaying` is now determined from orchestration history.
- Raised the minimum supported Python version to 3.10 and dropped Python 3.9.
- Updated dependencies to address known CVEs.

## 1.5.0 - 2026-02-04

### Added

- Added orchestration version overrides to orchestration-start APIs.
- Propagated `FunctionInvocationId` through durable client HTTP operations for
  log correlation.

### Changed

- Reused `aiohttp.ClientSession` instances to reduce connection contention.
- Renamed and expanded the OpenAI Agent SDK integration preview.

## 1.4.0 - 2025-09-24

### Added

- Added the OpenAI Agent SDK integration preview for durable, stateful agents.

### Changed

- Corrected the integration name and updated its documentation and samples.

## 1.4.0rc2 - 2025-09-23

- Published a release candidate of the OpenAI Agent SDK integration preview
  with an OpenAI compatibility note.

## 1.3.3 - 2025-08-21

### Added

- Added the `version` property to `DurableOrchestrationContext`.

### Changed

- Updated `aiohttp` to 3.12.14.

## 1.3.2 - 2025-06-17

### Fixed

- Fixed long timers when using Durable Task Scheduler or MSSQL storage
  providers.

## 1.3.1 - 2025-06-12

### Fixed

- Added dependencies omitted from 1.3.0 so the package installs successfully.
- Corrected package metadata to consistently require Python 3.9 or later.

## 1.3.0 - 2025-06-12 [YANKED]

This release was yanked from PyPI because required dependencies were missing.
Use 1.3.1 or later instead.

### Added

- Added support for long timers.
- Added helpers for unit testing orchestrators, entities, and durable clients.
- Added OpenTelemetry distributed tracing for orchestrations and entities.

### Changed

- Raised the minimum supported Python version to 3.9.
- Updated `requests` and `aiohttp`.

### Fixed

- Fixed `task_any` returning the same task multiple times in some cases.
- Improved handling of exceptions without an error message.

## 1.2.10 - 2024-10-22

### Changed

- Improved `call_http` content handling.
- Made `EntityId` equality compare entity names and keys.

### Fixed

- Fixed orchestrators returning JSON-serializable objects.
- Improved the error raised for invalid orchestration output.

## 1.2.9 - 2024-02-14

### Added

- Added durable client APIs for suspending and resuming orchestrations.

### Fixed

- Fixed deserialization of history events whose result is `None`.

## 1.2.8 - 2023-11-07

### Fixed

- Added a compatibility layer for the new `azure-functions` Settings API,
  fixing the startup failure introduced in 1.2.7.

## 1.2.7 - 2023-11-06 [YANKED]

This release was yanked from PyPI because it could fail during application
startup. Use 1.2.8 or later instead.

### Changed

- Added support for the new `azure-functions` Settings API.

## 1.2.6 - 2023-09-07

### Fixed

- Prevented already scheduled tasks from being added to the open-tasks list.

## 1.2.5 - 2023-08-08

### Fixed

- Allowed repeated `task_any` calls over progressively smaller lists of
  already scheduled tasks.

## 1.2.4 - 2023-06-15

### Added

- Added initial Durable Functions blueprint support.
- Added safer activity and sub-orchestrator invocation by function name for
  the Python v2 programming model.

## 1.2.3 - 2023-05-03

### Changed

- Improved the error message returned by the durable client `terminate` API.

## 1.2.2 - 2023-01-25

### Fixed

- Exported the Python v2 programming model APIs only when the installed Azure
  Functions worker supports them.

## 1.2.1 - 2022-12-06

### Fixed

- Raised the minimum `azure-functions` dependency to 1.12.0 for Python v2
  programming model support.

## 1.2.0 - 2022-12-06

### Added

- Added preview support for the Azure Functions Python v2 programming model.

## 1.1.6 - 2022-08-04

### Fixed

- Fixed a regression in the `is_replaying` flag.
- Allowed subtasks to be yielded multiple times.

## 1.1.5 - 2022-07-01

### Changed

- Excluded the `azure` namespace package from builds to support dependency
  isolation in the Azure Functions Python worker.

## 1.1.4 - 2022-05-24

### Fixed

- Allowed timers in `task_all` and `task_any` compound tasks to be cancelled
  safely.
- Fixed orchestrations becoming stuck after the final failure of a retry API.

## 1.1.3 - 2021-11-09

### Fixed

- Allowed entity operation timeouts to be caught by orchestrators.

## 1.1.2 - 2021-09-24

### Fixed

- Allowed entity operation exceptions to be caught by orchestrators.
- Added missing timer task properties.

## 1.1.1 - 2021-09-14

### Fixed

- Fixed an edge case in retry APIs after a task failure.
- Allowed `task_all` to accept an empty task list.

## 1.1.0 - 2021-08-17

### Changed

- Replaced orchestration replay with a linear-time algorithm for improved
  performance at scale.

### Fixed

- Fixed string input serialization in `continue_as_new`.

## 1.0.3 - 2021-07-22

### Fixed

- Fixed nondeterminism errors when passing a fixed instance ID to a
  sub-orchestration.

## 1.0.1 - 2021-06-25

### Added

- Added `read_entity_state` to `DurableOrchestrationClient`.

### Changed

- Added support for the newer orchestration replay algorithm.

### Fixed

- Prevented tasks from being scheduled again when yielded more than once.

## 1.0.0 - 2021-03-05

First stable release of Durable Functions for Python.

### Added

- Added `new_guid` for deterministic UUID generation.
- Exported `OrchestrationRuntimeStatus` for status comparisons.
- Added a warning for applications configured with Extension Bundles v1.

## 1.0.0b12 - 2020-12-19

### Added

- Added Durable Entities support.

### Changed

- Dropped support for Extension Bundles v1.

### Fixed

- Fixed serialization of `datetime` objects.
- Fixed intermittent `None` values from `current_utc_datetime`.

## 1.0.0b11 - 2020-11-19

### Fixed

- Added custom object serialization to `call_activity_with_retry`.

## 1.0.0b10 - 2020-10-20

### Fixed

- Fixed managed identity token source metadata for end-to-end authentication.

## 1.0.0b9 - 2020-09-18

### Fixed

- Improved out-of-process error reporting so SDK errors are surfaced instead
  of a generic null-reference error.

## 1.0.0b8 - 2020-09-14

### Added

- Added the experimental rewind API.
- Added enum-based orchestration runtime statuses.
- Added the `is_replaying` flag.

### Fixed

- Fixed local `purge_instance_history` failures.
- Improved retry behavior to prevent nondeterminism after errors.

## 1.0.0b7 - 2020-08-05

### Added

- Added sub-orchestrations.
- Added `create_http_management_payload`.
- Added type annotations and improved IntelliSense.

### Fixed

- Fixed `continue_as_new` failing to restart an orchestrator.
- Fixed Boolean return-value serialization.
- Fixed timer matching for closely spaced timestamps.

## 1.0.0b6 - 2020-06-18

### Added

- Added the `create_timer` API.

## 1.0.0b5 - 2020-06-11

### Added

- Added custom object serialization.
- Added custom orchestration status.

## 1.0.0b4 - 2020-03-19

- Republished the third beta to correct the release pipeline.

## 1.0.0b3 - 2020-03-19

- Validated the automated PyPI release pipeline.

## 1.0.0b2 - 2020-03-14

### Fixed

- Removed incorrect `staticmethod` declarations.

## 1.0.0b1 - 2020-03-13

Initial public beta of Durable Functions for Python.

### Added

- Added function chaining, fan-out/fan-in, asynchronous HTTP APIs, and human
  interaction orchestration patterns.
- Added orchestration APIs for activities, retries, compound tasks, external
  events, HTTP calls, instance management, history queries, and purging.
