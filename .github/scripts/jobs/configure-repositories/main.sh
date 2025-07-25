#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/repositories.sh
source .github/scripts/workspace.sh
source .github/scripts/labels.sh

# ------------------------------------------------------------------------------
# Static variables.
# ------------------------------------------------------------------------------

repo_descriptor=".github/scripts/jobs/configure-repositories/repository.json"
exit_code=0

# ------------------------------------------------------------------------------
# Utility functions.
# ------------------------------------------------------------------------------

function check_repo_descriptor_schema() {
  local repo_descriptor_schema="$(
    realpath --relative-to="." "$(
      dirname "$repo_descriptor"
    )/$(
      jq -r '.["$schema"]' "$repo_descriptor"
    )"
  )"

  pip install check-jsonschema==0.33.* >/dev/null

  check-jsonschema --schemafile="$repo_descriptor_schema" "$repo_descriptor"
}

function check_repo_descriptor_has_predefined_labels() {
  local labels=(
    "$cfl_bot_ignore_label"
    "$ready_for_review_label"
  )

  for label in "${labels[@]}"; do
    if ! eval_bool "$(
      jq '.labels.individual | has("'"$label"'")' "$repo_descriptor"
    )"; then
      exit=1 echo_error "Label: \"$label\" is missing in \"$repo_descriptor\"."
    fi
  done
}

function merge_individual_and_group_labels() {
  jq '
    .labels.individual + (
      .labels.group |
      [.[] | .colour as $colour | .labels | map_values(.colour = $colour)] |
      add
    )
  ' "$repo_descriptor"
}

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
  check_repo_descriptor_schema

  check_repo_descriptor_has_predefined_labels

  local labels="$(merge_individual_and_group_labels)"
  local labels_length="$(echo "$labels" | jq 'length')"
  echo_info "Discoverd $labels_length labels."

  if [ "$labels_length" -gt 0 ]; then
    labels="$labels" process_repo "$REPO_NAME"
    labels="$labels" process_workspace_submodules "process_repo"
  fi
}

function handle_workflow_dispatch_event() { handle_schedule_event; }

function handle_push_event() { handle_schedule_event; }

# ------------------------------------------------------------------------------
# Entrypoint.
# ------------------------------------------------------------------------------

handle_event "$@"

exit $exit_code
