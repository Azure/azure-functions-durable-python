# Versioning

This directory contains a Function app that demonstrates how to make changes to an orchestrator function without breaking existing orchestration instances.

The orchestrator function has two code paths:

1. The old path invoking `activity_a`.
2. The new path invoking `activity_b` instead.

While `defaultVersion` in `host.json` is set to `1.0`, the orchestrator will always follow the first path, producing the following output:

```
Orchestration version: 1.0
Suborchestration version: 1.0
Hello from A!
```

When `defaultVersion` in `host.json` is updated (for example, to `2.0`), *new orchestration instances* will follow the new path, producing the following output:

```
Orchestration version: 2.0
Suborchestration version: 2.0
Hello from B!
```

What happens to existing orchestration instances that were started before the `defaultVersion` change? Waiting for an external event in the middle of the orchestrator provides a convenient opportunity to emulate a deployment while orchestration instances are still running:

1. Create a new orchestration by invoking the HTTP trigger (`http_start`).
2. Wait for the orchestration to reach the point where it is waiting for an external event.
3. Stop the app.
4. Change `defaultVersion` in `host.json` to `2.0`.
5. Deploy and start the updated app.
6. Trigger the external event.
7. Observe that the orchestration output.

```
Orchestration version: 1.0
Suborchestration version: 2.0
Hello from A!
```

Note that the value returned by `context.version` is permanently associated with the orchestrator instance and is not impacted by the `defaultVersion` change. As a result, the orchestrator follows the old execution path to guarantee deterministic replay behavior.

However, the suborchestration version is `2.0` because it was invoked this suborchestration was created *after* the `defaultVersion` change.
