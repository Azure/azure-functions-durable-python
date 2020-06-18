# Changelog

All notable changes to this project will be documented in this file.

## 1.0.0b6

Create timer functionality available

## 1.0.0b5

Object serialization made available

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
