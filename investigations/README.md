# gRPC Investigations

## Introduction

This folder contains code which shows communication between cross language applications - C# and Python. It is primarly meant for upskilling and understanding the basics of gRPC communication between two different language plaforms and identify tools to support development.

## Tools used to build  this repository

This code was built on a Windows 10 PC. But the tooling can be considered cross platform.

- Microsoft Visual Studio 2019
- Microsoft Visual Studio Code
- Python 3.6.9 on a virtual environemnt enabled via Anaconda

## Structure of the code

The repository consists of three folders:

- **DotNetGrpc\DotNetGrpcService**: Contains the source code for the implementation of the gRPC server in C# on the .NET Core platform.

- **DotNetGrpc\DotNetGrpcClient**: Contains the source code for the gRPC client implemented in C# on the .NET Core Platform.

- **PythonGrpc**: Contains the source code for both the gRPC server and client and server using Python 3.6.

## Client/Server Communication

### gRPC Contract

The implementation on both the platform conform the simplest contract, defined by the default .NET template for gRPC Server.

The contract is defined in the ProtoBuf file ```greet.proto``` available in all the folders.

The contract is defined as follows:

- A ```Greeter``` service with a ```SayHello``` method.
  - The ```SayHello``` method accepts a object of type - ```HelloRequest``` and responds with object of the type - ```HelloReply```.
    - The object of type - ```HelloRequest``` contains a single field of ```string``` type called ```name```.
    - The object of the type - ```HelloReply``` contains a single field of ```string``` type called ```message```.

The code snippet from the protobuf file is shown as below:

 ``` protobuf
service Greeter {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply);
}

// The request message containing the user's name.
message HelloRequest {
  string name = 1;
}

// The response message containing the greetings.
message HelloReply {
  string message = 1;
}

 ```

## Communicating Across Platforms

The code exibhits the ```Greet``` contract being used to communicate across platforms. When you launch the gRPC client, they try to communicate with the both the servers by sending the ```HelloRequest``` message, with a name field (GreeterClient) and the servere responds with a ```HelloReply``` containing the mssage field, which is displayed by the client.

## Gotchas encountered during the investigation

It was very easy to get C# client and C# server communicating over the gRPC channel. The same was for Python client and server code. The challange came when it came time for them communicate with cross platform.

### Differences in startup

The .NET/C# client and server are configured, by default to communicate on secure HTTPS/TLS channel. Python server and client are not. In order to make the communication work, we had to resolve the differences.

### Resolving the difference - .NET/C# Server

In order to make the Python client work out of the box, the .NET gRPC server was configured to run on the unenrypted HTTP port.

To do this, the ```Kestrel``` section of the ```appsettings.json``` file needs to be created/modified as follows:

``` json
...
  
  "Kestrel": {
    "EndpointDefaults": {
      "Url": "http://*.5000",
      "Protocols": "Http2"
    }
  }

...

```

This allows HTTP communication on port 5000. This setting to be used for **DEVELOPMENT** environments.

More information on this issue can be found here on this [Github issue](https://github.com/grpc/grpc-dotnet/issues/564).

### Resolving the difference - .NET/C# Client

Now that unencrypted channel is also available on the .NET/C# Server, the .NET client also needs to modified to support this, when communicating with the .NET and the Python gRPC server.

To do that, add the following snippet of code, prior to creating a channel:

``` C#
AppContext.SetSwitch("System.Net.Http.SocketsHttpHandler.Http2UnencryptedSupport", true);
channel = GrpcChannel.ForAddress(grpcEndpointAddress);
```

More information of this and more can be found on the [Microsoft .NET gRPC Troubleshooting guide](https://docs.microsoft.com/en-US/aspnet/core/grpc/troubleshoot?view=aspnetcore-3.0).

## Running the servers

### .NET/C# gRPC Server

1. Modify the ```appsettings.json``` file, ```investigations\DotNetGrpc\DotNetGrpcServer``` folder, based on the section above.
2. Launch the command shell
3. Starting from the root of the repository, navigate to ```investigations\DotNetGrpc\DotNetGrpcServer``` folder.
4. When executing for the **first time**, on the command shell, run ```dotnet build```.
5. Once the command is executed successfully, run ```dotnet run```.

Sample Output of the .NET gRPC Server

``` shell
$ dotnet run
info: Microsoft.Hosting.Lifetime[0]
      Now listening on: http://localhost:5000
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
info: Microsoft.Hosting.Lifetime[0]
      Hosting environment: Development
info: Microsoft.Hosting.Lifetime[0]
      Content root path: C:\Projects\CSE\DurableFunctions\azure-functions-durable-python\investigations\DotNetGrpc\DotNetGrpcService 
info: Microsoft.AspNetCore.Hosting.Diagnostics[1]
```

### Python gRPC Server

1. Launch the command shell
2. Activate the virtual python environment (if applicable).
3. Starting from the root of the repository, navigate to ```investigations\PythonGrpc``` folder.
4. When executing for the **first time**, run ```pip install -r requirements.txt```
5. Once the command is executed successfully, run ```python greet_server.py```.

Sample Output of the .NET gRPC Server

``` shell
$ python greet_server.py
Starting gRPC Server on port 50051
Started. Waiting for client connections...
```

## Running the gRPC clients

**Note**
Prior to executing the gRPC clients, ensure that both the .NET/C# and Python gRPC Servers are running.

### .NET/C# Client

1. Launch the command shell
2. Starting from the root of the repository, navigate to ```investigations\DotNetGrpc\DotNetGrpcClient``` folder.
3. When executing for the **first time**, on the command shell, run ```dotnet build```.
4. Once the command is executed successfully, run ```dotnet run```.

Sample Execution of the .NET/C# client

```bash
$ dotnet run
Calling C# Endpoint...
Response: Hello GreeterClient-DotNet from .NET gRPC Server
Calling Python Endpoint...
Response: Hello GreeterClient-DotNet from Python gRPC Server

```

### Python Client

1. Launch the command shell
2. Activate the virtual python environment (if applicable).
3. Starting from the root of the repository, navigate to ```investigations\PythonGrpc``` folder.
4. When executing for the **first time**, run ```pip install -r requirements.txt```
5. Once the command is executed successfully, run ```python greet_client.py```.

Sample Execution of the Python client

```bash

$ python greet_client.py
Calling C# Endpoint...
Response: Hello GreeterClient-Python from .NET gRPC Server
Calling Python Endpoint...
Response: Hello GreeterClient-Python from Python gRPC Server

```

## Current State of client/server communications

| Servers    | C# Client | Python Client |
| ---------- | :--------:| :-------------:|
| **C# Server** | :heavy_check_mark:| :heavy_check_mark:|
| **Python Server** | :heavy_check_mark:| :heavy_check_mark:|

## Resources

- [Offical gRPC site](https://grpc.io)
- [gRPC Auth Guide](https://www.grpc.io/docs/guides/auth/)
- [gRPC with ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/grpc/?view=aspnetcore-3.0)
- [Microsoft .NET gRPC Troubleshooting guide](https://docs.microsoft.com/en-US/aspnet/core/grpc/troubleshoot?view=aspnetcore-3.0)
- [Krestel - Http2 support](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel?view=aspnetcore-3.0#http2-support)
- [PluralSight Course: Enhancing Application Communication with gRPC](https://app.pluralsight.com/library/courses/grpc-enhancing-application-communication/table-of-contents)
