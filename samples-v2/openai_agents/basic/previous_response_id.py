#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from agents import Agent, Runner


def main():
    agent = Agent(
        name="Memory Assistant",
        instructions="You are a helpful assistant with memory of previous conversations.",
    )

    # First conversation
    print("First interaction:")
    result1 = Runner.run_sync(agent, "My name is John and I like pizza.")
    print(f"Assistant: {result1.final_output}")
    
    # Note: In a real implementation, you would use the previous_response_id
    # to maintain conversation context across multiple runs
    print("\nSecond interaction (remembering previous context):")
    result2 = Runner.run_sync(agent, "What did I tell you about my food preferences?")
    print(f"Assistant: {result2.final_output}")
    
    return result2.final_output
