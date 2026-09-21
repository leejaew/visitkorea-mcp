#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
output="$project_dir/deployment/python-deps.tar.gz"
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

mkdir -p "$work_dir/site"
PIP_USER=0 python3.11 -m pip install \
  --target "$work_dir/site" \
  --ignore-installed \
  --break-system-packages \
  --no-cache-dir \
  -r "$project_dir/requirements.txt"

PYTHONPATH="$work_dir/site" python3.11 -c \
  'import httpx, mcp, starlette, uvicorn'

tar \
  --sort=name \
  --mtime='@0' \
  --owner=0 \
  --group=0 \
  --numeric-owner \
  -C "$work_dir/site" \
  -czf "$work_dir/python-deps.tar.gz" \
  .

mv "$work_dir/python-deps.tar.gz" "$output"
printf 'Created %s\n' "$output"