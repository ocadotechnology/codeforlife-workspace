#!/bin/bash

function process_workspace_submodules() {
  local process="$1"

  readarray -t names < <(
    grep '\[submodule ".*"\]' .gitmodules |
      sed -E 's/\[submodule "(.*)"\]/\1/'
  )

  for name in "${names[@]}"; do
    local path="$(git config --file .gitmodules "submodule.$name.path")"
    local url="$(git config --file .gitmodules "submodule.$name.url")"

    $process "$name" "$path" "$url"
  done
}
