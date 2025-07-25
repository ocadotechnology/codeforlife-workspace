#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/github.sh

# ------------------------------------------------------------------------------
# Utility functions.
# ------------------------------------------------------------------------------

function process_repo() {
  local repo_name="$1"

  echo_h1 "$repo_name"

  local repo="$(make_repo "$repo_name")"
  local index=1
  local return_code=0

  while read -r label; do
    local name="$(echo "$label" | jq -r '.key')"
    local colour="$(echo "$label" | jq -r '.value.colour')"
    local description="$(echo "$label" | jq -r '.value.description')"

    options="-n" echo_bold "($index/$labels_length)."
    index=$((index + 1))
    echo -n " \"$name\" "

    local all_outputs=$(
      gh label create "$name" \
        --repo="$repo" \
        --color="$colour" \
        --description="$description" \
        --force \
        2>&1
    )

    if [ $? -eq 0 ]; then
      echo_success "✔"
    else
      return_code=1
      echo_error "✗\n$all_outputs"
    fi
  done < <(echo "$labels" | jq -c 'to_entries | .[]')

  return $return_code
}

# ------------------------------------------------------------------------------
# Event handlers.
# Must follow the naming convention "handle_{event_name}_event".
# ------------------------------------------------------------------------------

function handle_schedule_event() {
  process_repo "$REPO_NAME"
  process_workspace_submodules "process_repo"
}

function handle_workflow_dispatch_event() { handle_schedule_event; }

function handle_push_event() { handle_schedule_event; }

# ------------------------------------------------------------------------------
# Entrypoint.
# ------------------------------------------------------------------------------

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
labels_length="$(echo "$labels" | jq 'length')"

echo_info "Discoverd $labels_length labels."

if [ "$labels_length" -gt 0 ]; then handle_event; fi
