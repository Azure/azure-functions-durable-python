import json
import random

random.seed(10)

def main(phoneNumber: str, message):
  payload = {
    "body": f"Hey! You may want to check on your repo, there are too many open issues",
    "to": phoneNumber
  }

  message.set(json.dumps(payload))
  return "Message sent!"
