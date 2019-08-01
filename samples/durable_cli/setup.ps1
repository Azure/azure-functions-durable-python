$CLI_ZIP_NAME = "AzureFunctionsCLI.zip"
$CLI_ZIP_LOCATION = "https://github.com/Azure/azure-functions-core-tools/releases/download/2.7.1480/Azure.Functions.Cli.win-x64.2.7.1480.zip"
$DURABLE_EXTENSION_FOLDER = "$PSScriptRoot/Extensions"
$EXTENSION_ZIP_LOCATION = "$PSScriptRoot/$CLI_ZIP_NAME"
$PYTHON_WORKER_GITHUB_PATH = "https://github.com/Azure/azure-functions-python-worker.git"
$PYTHON_BRANCH_NAME = "durable-hack"
$PYTHON_WORKER_LOCATION = "$PSScriptRoot/PythonWorker"
$PYTHON_WORKER_REPLACE_FROM = "$PSScriptRoot/PythonWorker/azure/functions_worker"
$PYTHON_WORKER_REPLACE_TO = "$PSScriptRoot/FuncCoreTools/workers/python/deps/azure"
$global:CLI_EXTRACTION_PATH = "$PSScriptRoot/FuncCoreTools"

$exist = Test-Path "$PSScriptRoot/$CLI_ZIP_NAME" -PathType Leaf
if (-not $exist) {
    Invoke-WebRequest -Method Get -Uri "$CLI_ZIP_LOCATION" -OutFile "$PSScriptRoot/$CLI_ZIP_NAME"
}

$exist = Test-Path "$CLI_EXTRACTION_PATH" -PathType Container
if (-not $exist) {
    Expand-Archive -Path "$EXTENSION_ZIP_LOCATION" -DestinationPath "$CLI_EXTRACTION_PATH" -Force
}

$exist = Test-Path "$PYTHON_WORKER_LOCATION" -PathType Container
if (-not $exist) {
    git clone --depth 1 --branch "$PYTHON_BRANCH_NAME" "$PYTHON_WORKER_GITHUB_PATH" "$PYTHON_WORKER_LOCATION"
}

Copy-Item -Path "$PYTHON_WORKER_REPLACE_FROM" -Destination "$PYTHON_WORKER_REPLACE_TO" -Recurse -Force

Write-Host -ForegroundColor Yellow "Use 'func --help' to get information on how to run this customized func tool"
Write-Host -ForegroundColor Yellow "You may also want to run ./Setup.ps1 to activate this customized func tool in other powershell windows"

function global:func() {
    Param (
        [parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Varargs
    )

    $exe_path = "$CLI_EXTRACTION_PATH\func.exe"
    $path_exist = Test-Path -Path "$exe_path" -PathType Leaf
    Write-Host -ForegroundColor Yellow "Using $exe_path"
    if ($path_exist) {
        if ($Varargs.Count -gt 0) {
            Start-Process -FilePath "$exe_path" -NoNewWindow -Wait -ArgumentList $Varargs
        } else {
            Start-Process -FilePath "$exe_path" -NoNewWindow -Wait
        }
    }
}
