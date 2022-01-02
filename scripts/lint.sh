#!/bin/sh

set -eu

if ! [ -x "$(command -v black)" ]; then
  echo >&2 "error: black is not installed"
  exit 1
fi
if ! [ -x "$(command -v isort)" ]; then
  echo >&2 "error: isort is not installed"
  exit 1
fi

cd "$(dirname "$0")/.."
files=$(find * -name '*.py')
isort --profile black --float-to-top $files
black $files
