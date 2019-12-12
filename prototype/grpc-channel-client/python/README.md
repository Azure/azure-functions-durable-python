# Python Durable Function gRPC Client Prototype

## Introduction

This is a protoype code to invoke the Durable Functions gRPC service using Python.

## Running the code

1. Create a Python virtual environment. (recommended)
2. Activate your Python virtual environment.
3. Install the required packages using the following command:

     ```bash
        pip install -r requirements.txt
     ```

4. Run the Python gRPC client, with the following command:

   ```bash
        python durable_functions_grpc_client.py
   ```

## Generation python code from proto

After activating your Python virtual environment, run this code to generate the python files from the Protobuf definition:

``` bash
 pip install -r requirements.txt
 python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/DurableFunctions.proto
```
