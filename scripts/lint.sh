#!/usr/bin/env bash

set -e
set -x

mypy app
ruff check app tests scripts
ruff format app tests --check
