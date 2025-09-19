#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import random
from typing import Any

from pydantic import BaseModel

from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool


class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} started")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended with output {output}"
        )

    async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {source.name} handed off to {agent.name}"
        )

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} started tool {tool.name}"
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended tool {tool.name} with result {result}"
        )


###


@function_tool
def random_number(max: int) -> int:
    """
    Generate a random number from 0 to max (inclusive).
    """
    return random.randint(0, max)


@function_tool
def multiply_by_two(x: int) -> int:
    """Simple multiplication by two."""
    return x * 2


class FinalResult(BaseModel):
    number: int


multiply_agent = Agent(
    name="Multiply Agent",
    instructions="Multiply the number by 2 and then return the final result.",
    tools=[multiply_by_two],
    output_type=FinalResult,
    hooks=CustomAgentHooks(display_name="Multiply Agent"),
)

start_agent = Agent(
    name="Start Agent",
    instructions="Generate a random number. If it's even, stop. If it's odd, hand off to the multiply agent.",
    tools=[random_number],
    output_type=FinalResult,
    handoffs=[multiply_agent],
    hooks=CustomAgentHooks(display_name="Start Agent"),
)


def main():
    # Default max number for demo
    max_number = 250
    print(f"Generating random number between 0 and {max_number}")
    
    result = Runner.run_sync(
        start_agent,
        input=f"Generate a random number between 0 and {max_number}."
    )
    
    print("Done!")
    return result.final_output
