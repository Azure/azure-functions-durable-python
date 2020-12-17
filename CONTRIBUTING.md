# Contributor Onboarding
Thank you for taking the time to contribute to Durable Functions in [Python](https://www.python.org/)

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
- [Azure Functions Python Overview](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-azure-function-azure-cli?tabs=bash%2Cbrowser&pivots=programming-language-python)

## Pre-requisites

- OS
    - MacOS (or) Windows10 Ubuntu WSL
- Language Runtimes
    - .NET Core 2.0
    - \>= Python 3.6.x 

Note: Some ML libraries may not be compatible with newer Python versions. Make sure the library is compatible with the Python version.

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

### Python Virtual Environment

- Make sure a Python virtual environment is setup. If you are using VS Code, the Azure Functions Extension project will set one up for you. Alternately, you can set it up through command line as well.
Note: Conda based environments are not yet supported in Azure Functions.

### Setting up durable-py debugging


1.  Git clone your fork and use any starter sample from this [folder](https://github.com/Azure/azure-functions-durable-python/tree/dev/samples/) in your fork and open this folder in your VS Code editor.

2. Initialize this folder as an Azure Functions project using the VS Code Extension using these [instructions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-vs-code?pivots=programming-language-python). This step will create a Python virtual environment if one doesn't exist already.

3. Add a local.settings.json file

```
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your connection string>",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

4. Add a host.json file that looks like this

```
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[1.*, 2.0.0)"
  }
}
```

5. Optionally, if you want to specify a custom task hub name, say MyTaskHub, you can add that in the host.json file like this:

```
{
  "version": "2.0",
  "extensions": {
    "durableTask": {
      "hubName": "MyTaskHub"
    }
  },
  "extensionBundle": {
    ...
  }
}
```

6. For debugging, install the code using an editable pip install like this, in the VS Code Terminal:

```
pip install -e $REPOSITORY_ROOT/
```
where REPOSITORY_ROOT is the root folder of the azure-functions-durable-python repository 

7. Set breakpoints and click Run -> Start Debugging in VS Code. This should internally start the Azure Function using `func host start` command.

### Debugging end-to-end

If you want to debug into the Durable Task or any of the .NET bits, follow instructions below:

1. Open the Azure Storage Explorer and connect to the local storage emulator or the storage account you are using.
2. Make sure the Durable Python debugging is setup already and the debugger has started the `func` process.
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

This project uses a combination of Azure DevOps and GitHub Actions for CI/CD.

- For each PR request/merge, a continuous integration pipeline will run internally that performs linting and running unit tests on your PR/merge.
- A GitHub Action will also perform CI tasks against your PR/merge. This is designed to provide more control to the contributor.
- Releases into PyPI will be curated and performed by a CD pipeline internally. See the Getting Help Section to request a release.

## Getting help

 - Leave comments on your PR and @username for attention

### Requesting a release
- If you need a release into PyPI, request it by raising an issue and tagging @anthonychu or @davidmrdavid


