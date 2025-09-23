#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from agents import Agent, Runner


def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )

    result = Runner.run_sync(agent, "Tell me about recursion in programming.")
    return result.final_output
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.
