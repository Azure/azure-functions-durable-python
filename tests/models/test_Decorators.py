import azure.durable_functions as df
import azure.functions as func
import json


def get_user_code(app):
    functions = app.get_functions()
    assert len(functions) == 1
    return functions[0]

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