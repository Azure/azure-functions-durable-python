#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from pydantic import BaseModel
from typing import Optional

from agents import Agent, Runner


class WeatherInfo(BaseModel):
    city: str
    temperature: Optional[str] = None
    conditions: Optional[str] = None
    humidity: Optional[str] = None


def main():
    # Using non-strict mode allows the model to return partial or flexible output
    agent = Agent(
        name="Weather Assistant",
        instructions="Provide weather information for the requested city. Return as much detail as available.",
        output_type=WeatherInfo,
        # Note: In real implementation, you might set strict=False for more flexible output
    )

    result = Runner.run_sync(agent, "What's the weather like in Tokyo?")
    print(result.final_output)
    return result.final_output
