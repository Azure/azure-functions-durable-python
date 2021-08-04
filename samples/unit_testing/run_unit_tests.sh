#! /usr/bin/bash

# Bash script to run all unit tests from tests folder.
# Make sure the test name is of the format "test_*.py"
TESTS="./subscription-manager/unit_tests"
for TEST_NAME in $TESTS/*
do
    # Remove non-tests
    if [[ $TEST_NAME = *"__init__"*  || $TEST_NAME = *"pycache"* ]]; then
        continue
    fi
    echo "Running $TEST_NAME ..."

    # Cut out the directory names and trim .py extension
    SUFFIX_NAME=$(echo $TEST_NAME | cut -d "/" -f 4 | cut -d "." -f 1)
    python -m unittest subscription-manager.unit_tests.$SUFFIX_NAME
done