
# wait_for_external_event()  
  

## **Samples**


1. Wait for a external event

2.  Wait for any of the external events

3. Wait for all of the external events

  

### **1. Wait for a external event**

```
def generator_function(context):
	approved = yield context.df.wait_for_external_event("Approval")
	if approved:
		return "approved"
	else:
		return "denied"
```

### **2. Wait for any of the external events**

```
def generator_function(context):
	event1 = context.df.wait_for_external_event("Event1")
	event2 = context.df.wait_for_external_event("Event2")
	event3 = context.df.wait_for_external_event("Event3")
	
	winner = yield context.df.task_any([event1, event2, event3])
	if winner == event1:
		#...
	elif winner == event2:
		#...
	elif winner == event3:
		#..

```

### **3. Wait for all of the external events**

```
def generator_function(context):
	gate1 = context.df.wait_for_external_event("Event1")
	gate2 = context.df.wait_for_external_event("Event2")
	gate3 = context.df.wait_for_external_event("Event3")
	
	yield context.df.task_all([gate1, gate2, gate3])
	yield context.df.call_activity("DurableActivity", "Hello")

```