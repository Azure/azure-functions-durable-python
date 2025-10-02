import argparse
import requests
import time
import sys


def main():
    parser = argparse.ArgumentParser(description='Customer Service Orchestration Client')
    parser.add_argument(
        '--start-url',
        default='http://localhost:7071/api/orchestrators/customer_service',
        help='The orchestrator start URL'
    )
    args = parser.parse_args()

    # Start the orchestration
    orchestration = requests.post(args.start_url).json()

    while True:
        # Wait for a prompt in the custom status
        while True:
            status = requests.get(orchestration['statusQueryGetUri']).json()
            
            if status['runtimeStatus'] == 'Completed':
                print(f"Orchestration completed.")
                sys.exit(0)
            
            if status['runtimeStatus'] not in ['Pending', 'Running']:
                raise Exception(f"Unexpected orchestration status: {status['runtimeStatus']}")
            
            if status.get('customStatus') and status['customStatus'] != 'Thinking...':
                break
            
            time.sleep(1)
        
        # Prompt the user for input interactively
        user_input = input(status['customStatus'] + ': ')
        
        # Send the user input to the orchestration as an external event
        event_url = orchestration['sendEventPostUri'].replace('{eventName}', 'UserInput')
        requests.post(event_url, json=user_input)
        
        time.sleep(2)


if __name__ == '__main__':
    main()
