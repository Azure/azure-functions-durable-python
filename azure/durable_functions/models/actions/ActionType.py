from enum import IntEnum


class ActionType(IntEnum):
    CallActivity: int = 0
    CallActivityWithRetry: int = 1
    CallSubOrchestrator: int = 2
    CallSubOrchestratorWithRetry: int = 3
    ContinueAsNew: int = 4
    CreateTimer: int = 5
    WaitForExternalEvent: int = 6
