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
      exit_code=1
      echo_error "✗\n$all_outputs"
    fi
  done < <(echo "$labels" | jq -c 'to_entries | .[]')
}

# ------------------------------------------------------------------------------
# Event handlers.
# Must follow the naming convention "handle_{event_name}_event".
# ------------------------------------------------------------------------------

function handle_schedule_event() {
  # Download the repository descriptor.
  local repo_descriptor=".github/repository.json"
  download_workspace_file "$repo_descriptor"

  # Dynamically insert cfl-bot's ignore label.
  echo "$(
    jq '
      .labels.individual["'"$cfl_bot_ignore_label"'"] = {
        "description": "Instructs @cfl-bot to ignore this issue.",
        "colour": "#000000"
      }
    ' "$repo_descriptor"
  )" >"$repo_descriptor"

  # Validate the the repository descriptor's schema.
  $(
    pip install check-jsonschema==0.33.*
    cd "$(dirname "$repo_descriptor")"
    check-jsonschema \
      --schemafile="$(jq -r '.["$schema"]' "$repo_descriptor")" \
      "$repo_descriptor"
  )

  # Merge individual and group labels.
  labels="$(
    jq '
      .labels.individual + (
        .labels.group |
        [.[] | .colour as $colour | .labels | map_values(.colour = $colour)] |
        add
      )
    ' "$repo_descriptor"
  )"

  local labels_length="$(echo "$labels" | jq 'length')"
  echo_info "Discoverd $labels_length labels."

  if [ "$labels_length" -gt 0 ]; then
    exit_code=0
    process_repo "$REPO_NAME"
    process_workspace_submodules "process_repo"
    exit $exit_code
  fi
}

function handle_workflow_dispatch_event() { handle_schedule_event; }

function handle_push_event() { handle_schedule_event; }

# ------------------------------------------------------------------------------
# Entrypoint.
# ------------------------------------------------------------------------------

handle_event "$@"
