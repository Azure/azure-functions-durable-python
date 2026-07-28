import sys

import azure.durable_functions as df
import azure.functions as func
import json


def get_user_code(app):
    functions = app.get_functions()
    assert len(functions) == 1
    return functions[0]


def get_built_function(app):
    """Return the built callable the worker introspects for binding type-checks.

    ``_add_rich_client`` wraps the user function; the wrapper is stored on the
    indexed ``Function`` object at ``._func``.
    """
    return get_user_code(app)._func

def assert_json(user_code, expected_dict):
    user_code_json = json.dumps(json.loads(str(user_code)), sort_keys=True)
    expected_json = json.dumps(expected_dict, sort_keys=True)
    assert user_code_json == expected_json
                     

def test_orchestration_trigger(app):

    @app.orchestration_trigger(context_name="my_context")
    def dummy_function(my_context):
        pass
    
    user_code = get_user_code(app)

    assert user_code.get_function_name() == "dummy_function"
    assert_json(user_code, {
        "scriptFile": "function_app.py",
        "bindings": [
            {
                "direction": "IN",
                "name": "my_context",
                "type": "orchestrationTrigger"
            }
        ]
    })

def test_orchestration_trigger_input_type_stashed(app):
    """Verify that input_type= on the decorator is stashed on the handle."""

    class MyInput:
        pass

    @app.orchestration_trigger(context_name="my_context", input_type=MyInput)
    def dummy_function(my_context):
        pass

    user_code = get_user_code(app)
    assert user_code.get_function_name() == "dummy_function"
    # The input type is stashed on the inner callable (the Orchestrator
    # handle) which lives at Function._func.
    assert getattr(user_code._func, "_df_input_type", None) is MyInput

def test_activity_trigger(app):

    @app.activity_trigger(input_name="my_input")
    def dummy_function(my_input):
        pass
    
    user_code = get_user_code(app)

    assert user_code.get_function_name() == "dummy_function"
    assert_json(user_code, {
        "scriptFile": "function_app.py",
        "bindings": [
            {
                "direction": "IN",
                "name": "my_input",
                "type": "activityTrigger"
            }
        ]
    })

def test_entity_trigger(app):

    @app.entity_trigger(context_name="my_context")
    def dummy_function(my_context):
        pass
    
    user_code = get_user_code(app)

    assert user_code.get_function_name() == "dummy_function"
    assert_json(user_code, {
        "scriptFile": "function_app.py",
        "bindings": [
            {
                "direction": "IN",
                "name": "my_context",
                "type": "entityTrigger"
            }
        ]
    })

def test_durable_client_input(app):

    @app.durable_client_input(client_name="my_client")
    @app.route(route="myOrchestratorRoute")
    def dummy_function(req, my_client, message):
        pass
    
    user_code = get_user_code(app)

    assert user_code.get_function_name() == "dummy_function"
    assert_json(user_code, {
        "scriptFile": "function_app.py",
        "bindings": [
            {
                "direction": "IN",
                "type": "httpTrigger",
                "authLevel": "ANONYMOUS",
                "name": "req",
                "route": "myOrchestratorRoute"
            },
            {
                "direction": "OUT",
                "name": "$return",
                "type": "http"
            },
            {
                "direction": "IN",
                "name": "my_client",
                "type": "durableClient"
            }
        ]
    })


def test_durable_client_input_annotation_overridden_to_str(app):
    """The client-binding parameter annotation reads as ``str`` on the built function.

    The worker type-checks the ``durableClient`` binding against the client
    parameter's annotation. ``_add_rich_client`` forces that annotation to
    ``str`` so the rich ``DurableOrchestrationClient`` object passes validation.

    On Python 3.14 (PEP 649/749) ``functools.wraps`` copies ``__annotate__``
    rather than the already-patched ``__annotations__`` dict, so the wrapper
    re-derives the original ``DurableOrchestrationClient`` annotation and binding
    validation fails (``FunctionLoadError`` -> host 503). This asserts the ``str``
    override survives on the wrapper the worker actually reads, via both the
    dict-based reader and the ``__annotate__``-based reader used on 3.14.
    """

    @app.durable_client_input(client_name="client")
    @app.route(route="orchestrators/{functionName}")
    async def dummy_function(req: func.HttpRequest,
                             client: df.DurableOrchestrationClient):
        pass

    built_fn = get_built_function(app)

    # Dict-based reader (used on <=3.13, still consulted on 3.14).
    assert built_fn.__annotations__["client"] is str

    # __annotate__-based reader: what the worker uses on Python 3.14.
    if sys.version_info >= (3, 14):
        import annotationlib
        annotations = annotationlib.get_annotations(
            built_fn, format=annotationlib.Format.FORWARDREF)
        assert annotations["client"] is str
