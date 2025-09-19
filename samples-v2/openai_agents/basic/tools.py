#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from pydantic import BaseModel

from agents import Agent, Runner, function_tool


class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str


@function_tool
def get_weather(city: str) -> Weather:
    """Get the current weather information for a specified city."""
    print("[debug] get_weather called")
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")


agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent.",
    tools=[get_weather],
)


def main():
    result = Runner.run_sync(agent, input="What's the weather in Tokyo?")
    print(result.final_output)
    return result.final_output
