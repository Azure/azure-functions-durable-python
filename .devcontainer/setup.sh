#!/usr/bin/env bash

export PIP_INDEX_URL="https://pkgs.dev.azure.com/azfunc/public/_packaging/upstream-public/pypi/simple/"
unset PIP_EXTRA_INDEX_URL

pip install -r requirements.txt
