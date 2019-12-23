# Durable Functions - Python Port - gRPC Prototype

## Introduction

This folder contains the **prototype** code which implements gRPC channel as part of the Durable Function Extension. This code demostrates the invocation of a durable orchestration function written in Javascript through a gRPC channel, with a python code.

## Pre-requsites

The development environment should have the following:

- Microsoft .NET Core 2.2 SDK
- Python 3.6.x
- Node 10.x
- Azure Functions Core Tools
- Azure Storage Emulator or a version of Azurite that supports Table storage
- Azure Storage Explorer

## Code Organization

The code is organized as follows:

- **azure-functions-durable-extension** : This folder contains the fork of the Azure Functions - Durable Extension code from Release version 1.8.3. The prototype version changes the version to 1.9.0 (Unreleased version). The version of Durable Function currently in release is 2.0.0.
- **grpc=channel-client** : This folder contains python code which uses the grpc channel opened Durable Extension to invoke a orchestrator function (written in Javascript).
- **js-durable-test**: This folder contains the Durable Function code written in JavaScript. It is changed to use the changed version of the Azure Functions Durable Functions Extension.
  
## Changes made to support gRPC channel

### Durable Functions Extension

The following steps were taken to develop this prototype:

1. Starting at ```azure-functions-durable-extension-folder``` folder.
2. Added gRPC and Google Protobuf NuGet packages to the C# project (```src/WebJobs.Extensions.DurableTask/WebJobs.Extensions.DurableTask.csproj```) as references.

    ``` xml
    <ItemGroup>
        <PackageReference Include="Google.Protobuf" Version="3.11.1" />
        <PackageReference Include="Grpc.Core" Version="2.25.0" />
        <PackageReference Include="Grpc.Tools" Version="2.25.0">
        <PrivateAssets>all</PrivateAssets>
        <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
        </PackageReference>
        <PackageReference Include="Microsoft.SourceLink.GitHub" Version="1.0.0-*" PrivateAssets="All" />
    </ItemGroup>
    ```

3. Defined the protobuf contracts to start a new orchestrator function. (See: ```src/WebJobs.Extensions.DurableTask/Listener/GRpc/protos/DurableFunctions.proto```)
4. Modified C# project (See: ```src/WebJobs.Extensions.DurableTask/WebJobs.Extensions.DurableTask.csproj```) to include generation of the gRPC contracts during build.

    ``` xml
    <ItemGroup>
        <Protobuf Include="Listener\GRpc\protos\DurableFunctions.proto" GrpcServices="Server" />
    </ItemGroup>
    ```

5. Implemented the gRPC service (See: ```src/WebJobs.Extensions.DurableTask/Listener/GRpc/DurableTaskServiceImpl.cs```)
6. Created a gRPC Service host (See: ```src/WebJobs.Extensions.DurableTask/Listener/GRpc/DurableTaskGrpcService.cs```)
7. Modified the ```DurableFunctionExtension``` class to support the creation of the gRPC service host and starting it in the _IExtensionConfigProvider.Initialize_ method.
8. Built and compiled the new code into the NuGet package.
9. Copied the built NuGet package to a location on the disk.

### Javascript Durable Function

The following changes were made to the JavaScript durable function project to support use of the newly built Durable Extensions.

1. Navigate to ```js-durabletest``` folder.
2. Added a C# project file in the root folder called ```extensions.csproj```, with the following contents:

    ``` xml
    <Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <TargetFramework>netstandard2.0</TargetFramework>
        <WarningsAsErrors></WarningsAsErrors>
        <DefaultItemExcludes>**</DefaultItemExcludes>
    </PropertyGroup>
    <ItemGroup>
        <PackageReference Include="Microsoft.Azure.WebJobs.Script.ExtensionsMetadataGenerator" Version="1.1.0" />
        <PackageReference Include="Microsoft.Azure.WebJobs.Extensions.DurableTask" Version="1.9.0" />
    </ItemGroup>
    </Project>

    ```

3. Modify the ```host.json``` file to exclude extension bundle. The contents of the host.json should look like this

    ```json
    {
        "version": "2.0",
        "extensions": {
            "durableTask": {
            }
        }
    }

    ```

4. Add a ```extensions.json``` file to include the mapping of bindings to the extension. The code should look like this:

    ```json
    [
        {
            "id": "Microsoft.Azure.WebJobs.Extensions.DurableTask",
            "version": "1.9.0",
            "name": "DurableTask",
            "bindings": [
                "activitytrigger",
                "orchestrationtrigger",
                "orchestrationclient"
            ]
        }

    ]

    ```

5. Add a ```NuGet.config``` file to indicate the new location to obtain the modified NuGet Package. **NOTE:** Modify the value of - _"Local Repo"_ to match the location on your disk where the Durable Task Extension NuGet are stored.

    ``` xml
        <?xml version="1.0" encoding="utf-8"?>
        <configuration>
            <packageSources>
                <add key="Local Repo" value="C:/Projects/CSE/DurableFunctions/NuGetPackages" />
                <add key="NuGet official package source" value="https://api.nuget.org/v3/index.json" />
            </packageSources>
            <packageRestore>
                <add key="enabled" value="True" />
            </packageRestore>
        </configuration>
    ```

6. Run the ```dotnet build``` command to allow the function host to use the modified Durable Extension.

## Running the code

### Azure Functions Host

1. Navigate to ```js-durabletest``` folder.
2. Configure the Azure Functions host to use local storage.
3. Start the Azure Storage Emulator (or Azurite).
4. Run the Azure Functions Host using the ```func host start``` command.
5. The output should be similar to below:

    ``` bash
                 %%%%%%
                 %%%%%%
            @   %%%%%%    @
          @@   %%%%%%      @@
       @@@    %%%%%%%%%%%    @@@
     @@      %%%%%%%%%%        @@
       @@         %%%%       @@
         @@      %%%       @@
           @@    %%      @@
                %%
                %

    Azure Functions Core Tools (2.7.1948 Commit hash: 29a0626ded3ae99c4111f66763f27bb9fb564103)
    Function Runtime Version: 2.0.12888.0

    ...

    [12/23/2019 1:48:56 PM] Initializing extension with the following settings: Initializing extension with the following settings:
    [12/23/2019 1:48:56 PM] AzureStorageConnectionStringName: , MaxConcurrentActivityFunctions: 80, MaxConcurrentOrchestratorFunctions: 80, PartitionCount: 4, ControlQueueBatchSize: 32, ControlQueueVisibilityTimeout: 00:05:00, WorkItemQueueVisibilityTimeout: 00:05:00, ExtendedSessionsEnabled: False, EventGridTopicEndpoint: , NotificationUrl: http://localhost:7071/runtime/webhooks/durabletask, TrackingStoreConnectionStringName: , MaxQueuePollingInterval: 00:00:30, LogReplayEvents: False. InstanceId: . Function: . HubName: DurableFunctionsHub. AppName: . SlotName: . ExtensionVersion: 1.9.0. SequenceNumber: 0.
    [12/23/2019 1:48:56 PM] Starting Durable Task - gRPC server on - 50051

    ...

    Now listening on: http://0.0.0.0:7071
    Application started. Press Ctrl+C to shut down.
    [12/23/2019 1:49:03 PM] Host lock lease acquired by instance ID '000000000000000000000000F6D26648'.
    ```

6. Note the start of the version of the Durable Function Extension matches the modifed version of 1.9.0.
7. Also note the gRPC server starting on port - 50051.
8. These are indications that the code has loaded up properly and available to invoke the durable functions using the gRPC channel.

### Invoking the Python code

1. Once the Azure Function host has started, navigate to the ```grpc-channel-client/python``` folder.
2. Activate the python virtual environment, if applicable.
3. Restore the python packages, if running the code for the first time using the ```pip install -r requirements.txt``` command.
4. Open the Azure Storage Explorer to view the contents of the table Storage in local storage emulator.
5. If executing durable functions for the first time, the tables - ```DurableFunctionHubHistory``` and ```DurableFunctionsHubInstances``` may not be present or may be empty. Example shown below:

   ![Storage Emulator - Before Execution](images\001_StorageExplorer_BeforeExecution.png)

6. On the command line enter the command - ```python durable_functions_grpc_client.py```
7. The sucessful execution returns the following output:

    ``` bash
    id: "1"
    StatusQueryGetUri: "https://localhost/Status/1"
    SendEventPostUri: "https://localhost/Event/1"
    TerminatePostUri: "https://localhost/terminate/1"
    RewindPostUri: "http://localhost/Rewind/1"
    PurgeHistoryDeleteUri: "http://localhost/Delete/1"
    ```

8. After the sucessful execution of the code, view the contents of the table storage and it may look similar to below:

     ![Storage Emulator - After Execution](images\002_StorageExplorer_AfterExecution.png)

9. This shows sucessful demostration of execution of the JavaScript durable function orchestration function using the gRPC channel using a Python client.
