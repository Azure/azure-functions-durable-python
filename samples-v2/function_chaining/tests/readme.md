# Durable Functions Sample – Unit Tests (Python)

This directory contains a simple **unit test** for the sample [Durable Azure Functions](https://learn.microsoft.com/azure/azure-functions/durable/durable-functions-overview) written in Python. This test demonstrates how to validate the logic of the orchestrator function in isolation using mocks.

## Prerequisites

- Python 
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) (for running functions locally)  
- [pytest](https://docs.pytest.org) for test execution  
- VS Code with the **Python** and **Azure Functions** extensions (optional but recommended)

---

## Running Tests from the Command Line

1. Open a terminal or command prompt.
2. Navigate to the project root (where your `requirements.txt` is).
3. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate   # On Windows
source .venv/bin/activate  # On macOS/Linux
```
Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest 
```

## Running Tests in Visual Studio Code
1. Open the project folder in VS Code.
2. Make sure the Python extension is installed.
3. Open the Command Palette (Ctrl+Shift+P), then select:
```
Python: Configure Tests
```
4. Choose pytest as the test framework.
5. Point to the tests/ folder when prompted.
6. Once configured, run tests from the Test Explorer panel or inline with the test code.

Notes
- Tests use mocks to simulate Durable Functions' context objects.
- These are unit tests only; no real Azure services are called.
- For integration tests, consider starting the host with func start.