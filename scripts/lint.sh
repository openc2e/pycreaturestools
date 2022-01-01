#!/bin/sh

set -eu

if ! [ -x "$(command -v black)" ]; then
  echo >&2 "error: black is not installed"
  exit 1
fi

topdir="$(dirname "$0")/.."
black "$topdir"
