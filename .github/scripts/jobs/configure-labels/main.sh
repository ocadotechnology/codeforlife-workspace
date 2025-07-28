#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/repositories.sh
source .github/scripts/workspace.sh
source .github/scripts/labels.sh

labels_descriptor=".github/descriptors/labels.json"
exit_code=0

function check_labels_descriptor_schema() {
  local labels_descriptor_schema="$(
    realpath --relative-to="." "$(
      dirname "$labels_descriptor"
    )/$(
      jq -r '.["$schema"]' "$labels_descriptor"
    )"
  )"

  pip install check-jsonschema==0.33.* >/dev/null

  check-jsonschema --schemafile="$labels_descriptor_schema" "$labels_descriptor"
}

function check_labels_descriptor_has_predefined_labels() {
  local labels=(
    "$cfl_bot_ignore_label"
    "$ready_for_review_label"
  )

  for label in "${labels[@]}"; do
    if ! eval_bool "$(
      jq '.individual | has("'"$label"'")' "$labels_descriptor"
    )"; then
      exit=1 echo_error "Label: \"$label\" is missing in \"$labels_descriptor\"."
    fi
  done
}

function merge_individual_and_group_labels() {
  jq '
    .individual + (
      .group |
      [.[] | .colour as $colour | .labels | map_values(.colour = $colour)] |
      add
    )
  ' "$labels_descriptor"
}

function configure_labels() {
  echo_h2 "labels"

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

function process_repo() {
  local repo_name="$1"

  echo_h1 "$repo_name"

  local repo="$(make_repo "$repo_name")"

  configure_labels
}

function main() {
  check_labels_descriptor_schema

  check_labels_descriptor_has_predefined_labels

  labels="$(merge_individual_and_group_labels)"
  labels_length="$(echo "$labels" | jq 'length')"
  echo_info "Discoverd $labels_length labels."

  if [ "$labels_length" -gt 0 ]; then
    process_repo "$REPO_NAME"
    process_workspace_submodules "process_repo"
  fi

  exit $exit_code
}

main
