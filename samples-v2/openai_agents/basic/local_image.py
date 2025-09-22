#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from agents import Agent, Runner


def main():
    # Note: In a real implementation, you would handle image upload/attachment
    # This simplified version demonstrates the pattern
    agent = Agent(
        name="Image Assistant", 
        instructions="You are a helpful assistant that can analyze images.",
    )

    # Simulated image analysis for the demo
    message = "I have uploaded a local image. Please describe what you see in it."
    
    # Note: In a real scenario, you would include the actual image data
    # For this demo, we'll simulate the response
    result = Runner.run_sync(agent, message)
    print(result.final_output)
    return result.final_output
