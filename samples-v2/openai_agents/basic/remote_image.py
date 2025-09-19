#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from agents import Agent, Runner


def main():
    agent = Agent(
        name="Remote Image Assistant",
        instructions="You are a helpful assistant that can analyze images from URLs.",
    )

    # Example with a hypothetical remote image URL
    image_url = "https://example.com/sample-image.jpg"
    message = f"Please analyze this image from the URL: {image_url}"
    
    # Note: In a real implementation, you would handle the remote image URL
    # and include it in the message or as an attachment
    result = Runner.run_sync(agent, message)
    print(result.final_output)
    return result.final_output
