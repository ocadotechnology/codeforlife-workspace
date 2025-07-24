#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/github.sh

repo_descriptor=".github/repository.json"
download_workspace_file "$repo_descriptor"

labels="$(
  jq '
    .labels.individual + (
      .labels.group |
      [.[] | .colour as $colour | .labels | map_values(.colour = $colour)] |
      add
    )
  ' "$repo_descriptor"
)"

function process_repo() {
  local repo_name="$1"

  local repo="$(make_repo "$repo_name")"

  echo "$labels" | jq -c 'to_entries | .[]' | while read -r label; do
    name="$(echo "$label" | jq -r '.key')"
    colour="$(echo "$label" | jq -r '.value.colour')"
    description="$(echo "$label" | jq -r '.value.description')"

    gh label create "$name" \
      --repo="$repo" \
      --color="$colour" \
      --description="$description" \
      --force

    echo_success "✔ $name"
  done
}

process_repo "$REPO_NAME"

process_workspace_submodules "process_repo"
