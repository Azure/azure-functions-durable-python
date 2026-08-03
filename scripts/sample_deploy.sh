#!/bin/bash

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFS_PYPI_INDEX="https://pkgs.dev.azure.com/azfunc/public/_packaging/upstream-public/pypi/simple/"
export PIP_INDEX_URL="$CFS_PYPI_INDEX"
unset PIP_EXTRA_INDEX_URL

echo "Checking for prerequisites..."
if ! type npm > /dev/null; then
    echo "Prerequisite Check 1: Install Node.js and NPM"
    exit 1
fi

if ! type dotnet > /dev/null; then
    echo "Prerequisite Check 2: Install .NET Core 2.1 SDK or Runtime"
    exit 1
fi

if ! type func > /dev/null; then
    echo "Prerequisite Check 3: Install Azure Functions Core Tools"
    exit 1
fi

echo "Pre-requisites satisfied..."

echo "Creating sample folders..."
DIRECTORY=/tmp/df_test
if [ ! -d "$DIRECTORY" ]; then
  mkdir "$DIRECTORY"
else
  rm -rf "$DIRECTORY"/*
fi

SAMPLE=function_chaining
cp -r "$REPOSITORY_ROOT/samples/$SAMPLE" "$DIRECTORY/"
cp "$REPOSITORY_ROOT/NuGet.config" "$DIRECTORY/NuGet.config"
cd "$DIRECTORY/$SAMPLE"
python -m venv env
source env/bin/activate

echo "Provide local path to azure-functions-durable-python clone:"
read lib_path
pip install "$lib_path/azure-functions-durable-python"
func init .
func extensions install
echo "Done"
