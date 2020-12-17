import json
import random

random.seed(10)

def main(phoneNumber, message):
  code = random.randint(0, 10000)
  payload = {
    "body": f"Your verification code is {code}",
    "to": phoneNumber
  }

  message.set(json.dumps(payload))
  code_str = str(code)
  return code_str
