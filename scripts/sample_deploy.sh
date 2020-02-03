 #!/bin/bash

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
  mkdir /tmp/df_test
else
  rm -rf /tmp/df_test/*
fi

SAMPLE=function_chaining
cp -r ../samples/$SAMPLE $DIRECTORY/
cd $DIRECTORY/$SAMPLE
python -m venv env
source env/bin/activate

echo "Provide local path to azure-functions-durable-python clone:"
read lib_path
pip install $lib_path/azure-functions-durable-python
func init .
func extensions install
echo "Done"

