#!/bin/sh

set -eu

python -m unittest discover --start-directory "$(dirname "$0")/../tests" --verbose
