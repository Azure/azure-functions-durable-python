# Durable Python API

## Function Chaining Pattern

It is recommended to use yield generators to avoid any non deterministic executions and have more control over what is getting yielded and to also have an imperative design

### Example 1: Explicit Generators

```
import logging
import azure.durable_functions.orchestrator as orchestrator

def function_chain():
    outputs = []
    task1 = yield orchestrator.call_activity("DurableActivity", "One")
    task2 = yield orchestrator.call_activity("DurableActivity", "Two")
    task3 = yield orchestrator.call_activity("DurableActivity", "Three")

    outputs.append(task1)
    outputs.append(task2)
    outputs.append(task3)

    return outputs

def main():
    logging.info(“Durable functions orchestration started..”)
    return orchestrator.create(function_chain)

```

### Example 2: Implicit Generators, more concise

```
import logging
import azure.durable_functions.orchestrator as orchestrator

my_vals=["Tokyo","Seattle","London"]

def function_chain():
    for val in my_vals:
        yield orchestrator.call_activity("DurableActivity",val)
        
def main():
    logging.info(“Durable functions orchestration started..”)
    return orchestrator.create(function_chain)

```

More Python syntactic sugar can be added or extended with the above using generator comprehensions

### Example 3: Generator Expressions, most concise

```
import logging
import azure.durable_functions.orchestrator as orchestrator

# Generator Expressions
my_vals=["Tokyo","Seattle","London"]
genexpr = (call_activity("Hello",i) for i in my_vals)

def function_chain():
    for val in my_vals:
        next(genexpr)
        
def main():
    logging.info(“Durable functions orchestration started..”)
    return orchestrator.create(function_chain)

```

