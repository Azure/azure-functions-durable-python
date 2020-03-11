# Contributor Onboarding
Thanks for taking the time to contribute to Durable Functions in [Python](https://www.python.org/)

## Table of Contents

- [What should I know before I get started?](#what-should-i-know-before-i-get-started)
- [Pre-requisites](#pre-requisites)
- [Pull Request Change Flow](#pull-request-change-flow)
- [Development Setup](#development-setup)
- [Pre Commit Tasks](#pre-commit-tasks)
- [Continuous Integration Guidelines & Conventions](#continuous-integration-guidelines-&-conventions)
- [Getting Help](#getting-help)



## What should I know before I get started
- [Durable Functions Overview](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
- [Durable Functions Application Patterns](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=csharp#application-patterns)

## Pre-requisites

- OS
    - MacOS (or) Windows10 Ubuntu WSL
- Language Runtimes
    - .NET Core 2.0
    - Python 3.6.x and higher
- Editor
    - Visual Studio Code
- Python 3 Tools (pip install)
    - [pytest](https://docs.pytest.org/en/latest/)
    - [nox](https://nox.thea.codes/en/stable/)
- Azure Tools
    - [Azure Storage Emulator](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-emulator) (or) [Create a storage account in Azure](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal)
    - [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools) v2.7.x and above.
    - [Azure Storage Explorer](https://azure.microsoft.com/en-us/features/storage-explorer/)

## Pull Request Change flow

The general flow for making a change to the library is:

1. 🍴 Fork the repo (add the fork via `git remote add me <clone url here>`
2. 🌳 Create a branch for your change (generally branch from dev) (`git checkout -b my-change`)
3. 🛠 Make your change
4. ✔️ Test your change
5. ⬆️ Push your changes to your fork (`git push me my-change`)
6. 💌 Open a PR to the dev branch
7. 📢 Address feedback and make sure tests pass (yes even if it's an "unrelated" test failure)
8. 📦 [Rebase](https://git-scm.com/docs/git-rebase) your changes into  meaningful commits (`git rebase -i HEAD~N` where `N` is commits you want to squash)
9. :shipit: Rebase and merge (This will be done for you if you don't have contributor access)
10. ✂️ Delete your branch (optional)

## Development Setup

### Visual Studio Code Extensions

The following extensions should be installed if using Visual Studio Code for debugging:

- Python support for Visual Studio Code (Python for VSCode extension)
- Azure Functions Extensions for Visual Studio Code v0.19.1 and above.
- autoDocString to generate documentation strings for Python API definitions.
 

### Setting up durable-py debugging

- Use starter sample from this folder (TBD: add folder name).

- If you want to debug a specific version of the Durable Extension, make the following changes: In host.json, remove the extensionsBundle portion to enable specific version debugging. 
- Provide a hub name (else remove the entire extensions portion to default to DurableFunctionsHub) Here's how the host.json should look like:

```
{
  "version": "2.0",
  "extensions": {
    "durableTask": {
      "hubName": "{hubName}"
    }
  }
}
```

- `func extensions install` (this will install an extensions.csproj that contains the version of DurableTask as seen below)

```xml <ItemGroup>
    <PackageReference Include="Microsoft.Azure.WebJobs.Extensions.DurableTask" Version="1.8.2" />
    <PackageReference Include="Microsoft.Azure.WebJobs.Script.ExtensionsMetadataGenerator" Version="1.1.0" />
  </ItemGroup>
```

### Debugging end-to-end

1. Open the Azure Storage Explorer and connect to the local storage emulator or the storage account you are using.
2. In the VSCode editor for durable-py click Debug -> Start Debugging. This will internally start `func host start` through core tools and provides the orchestrator client URL
3. In the VSCode editor for DurableTask, click Debug -> .NET Core Attach Process and search for `func host start` process and attach to it.
4. Add a breakpoint in both editors and continue debugging.

## Testing changes locally (Windows)

Follow all the steps above, use the Azure Storage Emulator for windows to simulate the storage account, and use Visual Studio to debug the .NET Durable Extension.

## Pre Commit Tasks

This library uses nox tooling for running unit tests and linting.

Make sure nox is pre-installed:
`pip install nox`

### Running unit tests

1. Add your unit tests under ./tests folder
2. Run: `nox --sessions tests`

### Running flake8 and flake8-docstring

Run:  `nox --sessions lint`

This library uses [numpy docstring convention](https://numpydoc.readthedocs.io/en/latest/format.html) for code documentation.


## Continuous Integration Guidelines & Conventions
TBD

## Getting help

 - Leave comments on your PR and @username for attention


