#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import azure.durable_functions as df
import azure.functions as func
import json
import pydantic
from typing import TypedDict
from agents import Agent, Runner
from azure.durable_functions.models import OrchestratorState
from azure.durable_functions.models.actions import CallActivityAction
from azure.durable_functions.models.ReplaySchema import ReplaySchema
from openai import BaseModel
from tests.orchestrator.orchestrator_test_utils import get_orchestration_state_result, assert_valid_schema, \
    assert_orchestration_state_equals
from tests.test_utils.ContextBuilder import ContextBuilder

app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name("openai_agent_hello_world")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_hello_world(context):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus."
    )

    result = Runner.run_sync(agent, "Tell me about recursion in programming.")

    return result.final_output;

#
# Run an agent that uses various tools.
#
class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str

    @staticmethod
    def from_json(data: str) -> "Weather":
        return Weather(**json.loads(data))

@app.activity_trigger(input_name="city")
def get_weather(city: str) -> Weather:
    print("[debug] get_weather called")
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")

@app.function_name("openai_agent_use_tool")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_use_tool(context):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        tools=[context.create_activity_tool(get_weather, retry_options=None)]
    )

    result = Runner.run_sync(agent, "Tell me the weather in Seattle.", )

    return result.final_output;

@app.activity_trigger(input_name="city", activity="get_weather_with_explicit_name")
def get_named_weather(city: str) -> Weather:
    print("[debug] get_weather called")
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")

@app.function_name("openai_agent_use_tool_with_explicit_name")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_use_tool_with_explicit_name(context):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        tools=[context.create_activity_tool(get_named_weather, retry_options=None)]
    )

    result = Runner.run_sync(agent, "Tell me the weather in Seattle.", )

    return result.final_output;

@app.function_name("openai_agent_return_string_type")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_return_string_type(context):
    return "Hello World"

class DurableModel:
    def __init__(self, property: str) -> None:
        self._property = property

    def to_json(self) -> str:
        return json.dumps({"property": self._property})

@app.function_name("openai_agent_return_durable_model_type")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_return_durable_model_type(context):
    model = DurableModel(property="value")

    return model

class TypedDictionaryModel(TypedDict):
    property: str

@app.function_name("openai_agent_return_typed_dictionary_model_type")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_return_typed_dictionary_model_type(context):
    model = TypedDictionaryModel(property="value")

    return model

class OpenAIPydanticModel(BaseModel):
    property: str

@app.function_name("openai_agent_return_openai_pydantic_model_type")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_return_openai_pydantic_model_type(context):
    model = OpenAIPydanticModel(property="value")

    return model

class PydanticModel(pydantic.BaseModel):
    property: str

@app.function_name("openai_agent_return_pydantic_model_type")
@app.orchestration_trigger(context_name="context")
@app.durable_openai_agent_orchestrator(model_retry_options=None)
def openai_agent_return_pydantic_model_type(context):
    model = PydanticModel(property="value")

    return model

model_activity_name = "run_model"

def base_expected_state(output=None, replay_schema: ReplaySchema = ReplaySchema.V1) -> OrchestratorState:
    return OrchestratorState(is_done=False, actions=[], output=output, replay_schema=replay_schema)

def add_activity_action(state: OrchestratorState, input_: str, activity_name=model_activity_name):
    action = CallActivityAction(function_name=activity_name, input_=input_)
    state.actions.append([action])

def add_activity_completed_events(
    context_builder: ContextBuilder, id_: int, result: str, is_played=False, activity_name=model_activity_name):
    context_builder.add_task_scheduled_event(name=activity_name, id_=id_)
    context_builder.add_orchestrator_completed_event()
    context_builder.add_orchestrator_started_event()
    context_builder.add_task_completed_event(id_=id_, result=json.dumps(result), is_played=is_played)

def test_openai_agent_hello_world_start():
    context_builder = ContextBuilder('test_openai_agent_hello_world_start')

    result = get_orchestration_state_result(
        context_builder, openai_agent_hello_world, uses_pystein=True)

    expected_state = base_expected_state()
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me about recursion in programming.\",\"role\":\"user\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_hello_world_completed():
    context_builder = ContextBuilder('test_openai_agent_hello_world_completed')
    add_activity_completed_events(context_builder, 0, '{"output":[{"id":"msg_68b9b2a9c67c81a38559c20c18fe86040a86c28ba39b53e8","content":[{"annotations":[],"text":"Skyscrapers whisper—  \\nTaxis hum beneath the lights,  \\nCity dreams don’t sleep.","type":"output_text","logprobs":null}],"role":"assistant","status":"completed","type":"message"}],"usage":{"requests":1,"input_tokens":27,"input_tokens_details":{"cached_tokens":0},"output_tokens":21,"output_tokens_details":{"reasoning_tokens":0},"total_tokens":48},"response_id":"resp_68b9b2a9461481a3984d0f790dd33f7b0a86c28ba39b53e8"}')

    result = get_orchestration_state_result(
        context_builder, openai_agent_hello_world, uses_pystein=True)

    expected_state = base_expected_state()
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me about recursion in programming.\",\"role\":\"user\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    expected_state._is_done = True
    expected_state._output = 'Skyscrapers whisper—  \nTaxis hum beneath the lights,  \nCity dreams don’t sleep.'
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_use_tool_activity_start():
    context_builder = ContextBuilder('test_openai_agent_use_tool_start')
    add_activity_completed_events(context_builder, 0, '{"output":[{"arguments":"{\\"args\\":\\"Seattle, WA\\"}","call_id":"call_mEdywElQTNpxAdivuEFjO0cT","name":"get_weather","type":"function_call","id":"fc_68b9ecc0ff9c819f863d6cf9e0a1b4e101011fd6f5f8c0a6","status":"completed"}],"usage":{"requests":1,"input_tokens":57,"input_tokens_details":{"cached_tokens":0},"output_tokens":17,"output_tokens_details":{"reasoning_tokens":0},"total_tokens":74},"response_id":"resp_68b9ecc092e0819fb79b97c11aacef2001011fd6f5f8c0a6"}')

    result = get_orchestration_state_result(
        context_builder, openai_agent_use_tool, uses_pystein=True)

    expected_state = base_expected_state()
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me the weather in Seattle.\",\"role\":\"user\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[{\"name\":\"get_weather\",\"description\":\"\",\"params_json_schema\":{\"properties\":{\"city\":{\"title\":\"City\",\"type\":\"string\"}},\"required\":[\"city\"],\"title\":\"get_weather_args\",\"type\":\"object\",\"additionalProperties\":false},\"strict_json_schema\":true}],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    add_activity_action(expected_state, "{\"args\":\"Seattle, WA\"}", activity_name="get_weather")
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_use_explicitly_named_tool_activity_start():
    context_builder = ContextBuilder('test_openai_agent_use_tool_start')
    add_activity_completed_events(context_builder, 0, '{"output":[{"arguments":"{\\"args\\":\\"Seattle, WA\\"}","call_id":"call_mEdywElQTNpxAdivuEFjO0cT","name":"get_named_weather","type":"function_call","id":"fc_68b9ecc0ff9c819f863d6cf9e0a1b4e101011fd6f5f8c0a6","status":"completed"}],"usage":{"requests":1,"input_tokens":57,"input_tokens_details":{"cached_tokens":0},"output_tokens":17,"output_tokens_details":{"reasoning_tokens":0},"total_tokens":74},"response_id":"resp_68b9ecc092e0819fb79b97c11aacef2001011fd6f5f8c0a6"}')

    result = get_orchestration_state_result(
        context_builder, openai_agent_use_tool_with_explicit_name, uses_pystein=True)

    expected_state = base_expected_state()
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me the weather in Seattle.\",\"role\":\"user\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[{\"name\":\"get_named_weather\",\"description\":\"\",\"params_json_schema\":{\"properties\":{\"city\":{\"title\":\"City\",\"type\":\"string\"}},\"required\":[\"city\"],\"title\":\"get_named_weather_args\",\"type\":\"object\",\"additionalProperties\":false},\"strict_json_schema\":true}],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    add_activity_action(expected_state, "{\"args\":\"Seattle, WA\"}", activity_name="get_weather_with_explicit_name")
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_use_tool_activity_completed():
    context_builder = ContextBuilder('test_openai_agent_use_tool_start')
    add_activity_completed_events(context_builder, 0, '{"output":[{"arguments":"{\\"args\\":\\"Seattle, WA\\"}","call_id":"call_mEdywElQTNpxAdivuEFjO0cT","name":"get_weather","type":"function_call","id":"fc_68b9ecc0ff9c819f863d6cf9e0a1b4e101011fd6f5f8c0a6","status":"completed"}],"usage":{"requests":1,"input_tokens":57,"input_tokens_details":{"cached_tokens":0},"output_tokens":17,"output_tokens_details":{"reasoning_tokens":0},"total_tokens":74},"response_id":"resp_68b9ecc092e0819fb79b97c11aacef2001011fd6f5f8c0a6"}')
    add_activity_completed_events(context_builder, 1, '{"__class__":"Weather","__module__":"function_app","__data__":"{\n \"city\": \"{\\\"args\\\":\\\"Seattle, WA\\\"}\",\n \"temperature_range\": \"14-20C\",\n \"conditions\": \"Sunny with wind.\"\n}"}')

    result = get_orchestration_state_result(
        context_builder, openai_agent_use_tool, uses_pystein=True)

    expected_state = base_expected_state()
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me the weather in Seattle.\",\"role\":\"user\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[{\"name\":\"get_weather\",\"description\":\"\",\"params_json_schema\":{\"properties\":{\"city\":{\"title\":\"City\",\"type\":\"string\"}},\"required\":[\"city\"],\"title\":\"get_weather_args\",\"type\":\"object\",\"additionalProperties\":false},\"strict_json_schema\":true}],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    add_activity_action(expected_state, "{\"args\":\"Seattle, WA\"}", activity_name="get_weather")
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me the weather in Seattle.\",\"role\":\"user\"},{\"arguments\":\"{\\\"args\\\":\\\"Seattle, WA\\\"}\",\"call_id\":\"call_mEdywElQTNpxAdivuEFjO0cT\",\"name\":\"get_weather\",\"type\":\"function_call\",\"id\":\"fc_68b9ecc0ff9c819f863d6cf9e0a1b4e101011fd6f5f8c0a6\",\"status\":\"completed\"},{\"call_id\":\"call_mEdywElQTNpxAdivuEFjO0cT\",\"output\":\"{\\\"__class__\\\":\\\"Weather\\\",\\\"__module__\\\":\\\"function_app\\\",\\\"__data__\\\":\\\"{\\n \\\"city\\\": \\\"{\\\\\\\"args\\\\\\\":\\\\\\\"Seattle, WA\\\\\\\"}\\\",\\n \\\"temperature_range\\\": \\\"14-20C\\\",\\n \\\"conditions\\\": \\\"Sunny with wind.\\\"\\n}\\\"}\",\"type\":\"function_call_output\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[{\"name\":\"get_weather\",\"description\":\"\",\"params_json_schema\":{\"properties\":{\"city\":{\"title\":\"City\",\"type\":\"string\"}},\"required\":[\"city\"],\"title\":\"get_weather_args\",\"type\":\"object\",\"additionalProperties\":false},\"strict_json_schema\":true}],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_use_tool_analysis_completed():
    context_builder = ContextBuilder('test_openai_agent_use_tool_start')
    add_activity_completed_events(context_builder, 0, '{"output":[{"arguments":"{\\"args\\":\\"Seattle, WA\\"}","call_id":"call_mEdywElQTNpxAdivuEFjO0cT","name":"get_weather","type":"function_call","id":"fc_68b9ecc0ff9c819f863d6cf9e0a1b4e101011fd6f5f8c0a6","status":"completed"}],"usage":{"requests":1,"input_tokens":57,"input_tokens_details":{"cached_tokens":0},"output_tokens":17,"output_tokens_details":{"reasoning_tokens":0},"total_tokens":74},"response_id":"resp_68b9ecc092e0819fb79b97c11aacef2001011fd6f5f8c0a6"}')
    add_activity_completed_events(context_builder, 1, '{"__class__":"Weather","__module__":"function_app","__data__":"{\n \"city\": \"{\\\"args\\\":\\\"Seattle, WA\\\"}\",\n \"temperature_range\": \"14-20C\",\n \"conditions\": \"Sunny with wind.\"\n}"}')
    add_activity_completed_events(context_builder, 2, '{"output":[{"id":"msg_68b9f4b09c14819faa62abfd69cb53e501011fd6f5f8c0a6","content":[{"annotations":[],"text":"The weather in Seattle, WA is currently sunny with some wind. Temperatures are ranging from 14°C to 20°C.","type":"output_text","logprobs":null}],"role":"assistant","status":"completed","type":"message"}],"usage":{"requests":1,"input_tokens":107,"input_tokens_details":{"cached_tokens":0},"output_tokens":28,"output_tokens_details":{"reasoning_tokens":0},"total_tokens":135},"response_id":"resp_68b9f4b00804819f9fe99eac95bd198e01011fd6f5f8c0a6"}')

    result = get_orchestration_state_result(
        context_builder, openai_agent_use_tool, uses_pystein=True)

    expected_state = base_expected_state()
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me the weather in Seattle.\",\"role\":\"user\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[{\"name\":\"get_weather\",\"description\":\"\",\"params_json_schema\":{\"properties\":{\"city\":{\"title\":\"City\",\"type\":\"string\"}},\"required\":[\"city\"],\"title\":\"get_weather_args\",\"type\":\"object\",\"additionalProperties\":false},\"strict_json_schema\":true}],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    add_activity_action(expected_state, "{\"args\":\"Seattle, WA\"}", activity_name="get_weather")
    add_activity_action(expected_state, "{\"input\":[{\"content\":\"Tell me the weather in Seattle.\",\"role\":\"user\"},{\"arguments\":\"{\\\"args\\\":\\\"Seattle, WA\\\"}\",\"call_id\":\"call_mEdywElQTNpxAdivuEFjO0cT\",\"name\":\"get_weather\",\"type\":\"function_call\",\"id\":\"fc_68b9ecc0ff9c819f863d6cf9e0a1b4e101011fd6f5f8c0a6\",\"status\":\"completed\"},{\"call_id\":\"call_mEdywElQTNpxAdivuEFjO0cT\",\"output\":\"{\\\"__class__\\\":\\\"Weather\\\",\\\"__module__\\\":\\\"function_app\\\",\\\"__data__\\\":\\\"{\\n \\\"city\\\": \\\"{\\\\\\\"args\\\\\\\":\\\\\\\"Seattle, WA\\\\\\\"}\\\",\\n \\\"temperature_range\\\": \\\"14-20C\\\",\\n \\\"conditions\\\": \\\"Sunny with wind.\\\"\\n}\\\"}\",\"type\":\"function_call_output\"}],\"model_settings\":{\"temperature\":null,\"top_p\":null,\"frequency_penalty\":null,\"presence_penalty\":null,\"tool_choice\":null,\"parallel_tool_calls\":null,\"truncation\":null,\"max_tokens\":null,\"reasoning\":null,\"metadata\":null,\"store\":null,\"include_usage\":null,\"response_include\":null,\"extra_query\":null,\"extra_body\":null,\"extra_headers\":null,\"extra_args\":null},\"tracing\":0,\"model_name\":null,\"system_instructions\":\"You only respond in haikus.\",\"tools\":[{\"name\":\"get_weather\",\"description\":\"\",\"params_json_schema\":{\"properties\":{\"city\":{\"title\":\"City\",\"type\":\"string\"}},\"required\":[\"city\"],\"title\":\"get_weather_args\",\"type\":\"object\",\"additionalProperties\":false},\"strict_json_schema\":true}],\"output_schema\":null,\"handoffs\":[],\"previous_response_id\":null,\"prompt\":null}")
    expected_state._is_done = True
    expected_state._output = 'The weather in Seattle, WA is currently sunny with some wind. Temperatures are ranging from 14°C to 20°C.'
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_string_serialization():
    context_builder = ContextBuilder('test_openai_agent_string_serialization')

    result = get_orchestration_state_result(
        context_builder, openai_agent_return_string_type, uses_pystein=True)

    expected_state = base_expected_state()
    expected_state._is_done = True
    expected_state._output = "Hello World"
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_durable_model_serialization():
    context_builder = ContextBuilder('test_openai_agent_durable_model_serialization')

    result = get_orchestration_state_result(
        context_builder, openai_agent_return_durable_model_type, uses_pystein=True)

    expected_state = base_expected_state()
    expected_state._is_done = True
    expected_state._output = DurableModel(property="value").to_json()
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_typed_dictionary_model_serialization():
    context_builder = ContextBuilder('test_openai_agent_typed_dictionary_model_serialization')

    result = get_orchestration_state_result(
        context_builder, openai_agent_return_typed_dictionary_model_type, uses_pystein=True)

    expected_state = base_expected_state()
    expected_state._is_done = True
    expected_state._output = json.dumps(TypedDictionaryModel(property="value"))
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_openai_pydantic_model_serialization():
    context_builder = ContextBuilder('test_openai_agent_openai_pydantic_model_serialization')

    result = get_orchestration_state_result(
        context_builder, openai_agent_return_openai_pydantic_model_type, uses_pystein=True)

    expected_state = base_expected_state()
    expected_state._is_done = True
    expected_state._output = OpenAIPydanticModel(property="value").to_json()
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)

def test_openai_agent_pydantic_model_serialization():
    context_builder = ContextBuilder('test_openai_agent_pydantic_model_serialization')

    result = get_orchestration_state_result(
        context_builder, openai_agent_return_pydantic_model_type, uses_pystein=True)

    expected_state = base_expected_state()
    expected_state._is_done = True
    expected_state._output = PydanticModel(property="value").model_dump_json()
    expected = expected_state.to_json()

    assert_valid_schema(result)
    assert_orchestration_state_equals(expected, result)
