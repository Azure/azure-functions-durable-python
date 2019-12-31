# Durable Python API

## Function Chaining Pattern

It is recommended to use yield generators to avoid any non deterministic executions and have more control over what is getting yielded and to also have an imperative design

### Example 1: Explicit Generators

```
import logging
import azure.durable_functions.orchestrator as orchestrator

def function_chain():

    result1 = yield orchestrator.call_activity("DurableActivity", "One")
    result2 = yield orchestrator.call_activity("DurableActivity", result1)
    final_result = yield orchestrator.call_activity("DurableActivity", result2)

    return final_result

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
    outputs = []
    for val in my_vals:
        outputs.append(yield orchestrator.call_activity("DurableActivity",val))
    return outputs
        
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
    outputs = []
    for val in my_vals:
        outputs.append(next(genexpr))
    return outputs
        
def main():
    logging.info(“Durable functions orchestration started..”)
    return orchestrator.create(function_chain)

```

