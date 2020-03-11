# Getting Started Guide


## Preliminary Requirements 
- Make sure you have the Azure account configured properly
- You are encouraged to use Visual Studio Code (VSC) as it has automated much of the functions outlined below
- You need the python, Azure and Azure functions plugin installed in VSC


## Create a new project
- Create a new project - by File -> New Window -> follow steps to a new project
- Click on the Azure icon on the left panel, and then click on the "lighting" for create a new function
- Select the desired Python version (recommneded 3.6), Anonymous, HttpTrigger, select name and simply all the default selection 
- Note: the last step is the same as calling func init and func new, but VSC also creates debug and setup configuration files which will be needed later
- Once everything is created - select the explorer view in order to edit files

## Change from regular functions to durable functions
- This step is needed as VSC does not support durable functions yet

- Edit host.json to look like the following:

	```
	{
	  "version": "2.0"
	}
	```
- Edit host.setting.json to look like the following
```
	{
	"IsEncrypted": false,
	"Values": {
		"AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=functiondurableart;AccountKey=7BleMuvzygluVLxJVSeTJMmRjfexZjjXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX;EndpointSuffix=core.windows.net",
			"FUNCTIONS_WORKER_RUNTIME": "python"
		}
	}
```

- Or if you have Azurite installed and configured:
```
	{
	"IsEncrypted": false,
	"Values": {
		"AzureWebJobsStorage": "UseDevelopmentStorage=true",
		"FUNCTIONS_WORKER_RUNTIME": "python"
	}
	}
```
-	Delete the HttpTrigger subdirectoy.  You should now be left with .venv (directory), .vscode (directory), host.json, local.settings.json, proxies.json, and requirements.txt

- Go to {worknig directory}/azure-functions-durable-python/samples/fan_out_fan_in, and copy the following directies as is to the new project directoy
	-	DurableTrigger
	- 	GetActivityCount
	- 	FanOutFanIn
	-	ParrotValue
	-	ShowMeTheSum

## Installing the Durable Function Required libs
-	In VSC terminal directoy, type the following:
```
	func extensions install
```

-	This call should create a file called extensions.csproj.   If it does not, you can create a file called exntesions.csproj with the following content:
```
	<Project Sdk="Microsoft.NET.Sdk">
	  <PropertyGroup>
	    <TargetFramework>netstandard2.0</TargetFramework>
		<WarningsAsErrors></WarningsAsErrors>
		<DefaultItemExcludes>**</DefaultItemExcludes>
	  </PropertyGroup>
	  <ItemGroup>
	    <PackageReference Include="Microsoft.Azure.WebJobs.Extensions.DurableTask" Version="2.1.0" />
	    <PackageReference Include="Microsoft.Azure.WebJobs.Script.ExtensionsMetadataGenerator" Version="1.1.0" />
	  </ItemGroup>
	</Project>
```

-	And then call:
```
	func extensions sync
```

Setup is now complete.  


# Running and Debugging
Click on the debug icon, followed by debug arrow ("Attach to Python Functions").  You should not see any errors in the output.  (all blue output).  

Open Postman, and POST the following command:
```
	http://localhost:7071/runtime/webhooks/durabletask/orchestrators/FanOutFanIn
```
-	It should return something like the following (no answer is returned as this is an async call):
```
	{
	    "id": "2249497badeb41abb3928e8a4020ef90",
	    "statusQueryGetUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/2249497badeb41abb3928e8a4020ef90?		taskHub=TestHubName&connection=Storage&code=2ioFvsUVhdOdetctK2M9xTgJLlAwAaLmpNqj6sXzfk0knLao0o/kXQ==",
	    "sendEventPostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/2249497badeb41abb3928e8a4020ef90/raiseEvent/{eventName}?taskHub=TestHubName&connection=Storage&code=2ioFvsUVhdOdetctK2M9xTgJLlAwAaLmpNqj6sXzfk0knLao0o/kXQ==",
	    "terminatePostUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/2249497badeb41abb3928e8a4020ef90/terminate?reason={text}&taskHub=TestHubName&connection=Storage&code=2ioFvsUVhdOdetctK2M9xTgJLlAwAaLmpNqj6sXzfk0knLao0o/kXQ==",
	    "purgeHistoryDeleteUri": "http://localhost:7071/runtime/webhooks/durabletask/instances/2249497badeb41abb3928e8a4020ef90?taskHub=TestHubName&connection=Storage&code=2ioFvsUVhdOdetctK2M9xTgJLlAwAaLmpNqj6sXzfk0knLao0o/kXQ=="
	}
```

-	Copy the URL from statusQueryGetUri variable, and do another POST, you should get the output:
```
{
    "name": "FanOutFanIn",
    "instanceId": "2249497badeb41abb3928e8a4020ef90",
    "runtimeStatus": "Completed",
    "input": null,
    "customStatus": null,
    "output": "Well that's nice 10",
    "createdTime": "2020-02-18T18:43:45Z",
    "lastUpdatedTime": "2020-02-18T18:43:51Z"
}
```



