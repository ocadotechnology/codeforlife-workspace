#!/bin/bash

function download_workspace_file() {
  local branch="${branch:-"main"}"
  local path="$1"
  local save_to="${2:-"$path"}"

  # Make parent directories.
  mkdir -p "$(dirname "$save_to")"

  # Download file.
  wget https://raw.githubusercontent.com/ocadotechnology/codeforlife-workspace/refs/heads/$branch/$path \
    -O "$save_to"
}
