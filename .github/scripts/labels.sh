#!/bin/bash

source .github/scripts/general.sh

labels_descriptor=".github/descriptors/labels.json"

ready_for_review_label="ready for review"
cfl_bot_ignore_label="bot ignore"

function make_label_filter() {
  local label_csv="$@"

  local label_filter="label:"
  if [ -n "$exclude" ] && eval_bool "$exclude"; then
    label_filter="-$label_filter"
  fi

  local label_count=0
  IFS=',' read -ra labels <<<"$label_csv"
  for label in "${labels[@]}"; do
    label="$(trim_spaces "$label")"
    if [ -n "$label" ]; then
      if [ "$label_count" -ne 0 ]; then label_filter+=","; fi
      label_filter+="\"$label\""
      ((label_count++))
    fi
  done

  echo "$label_filter"
}

function make_label_filter_from_descriptor_group() {
  local group="$1"

  local label_csv="$(
    jq -r '.group.'"$group"'.labels | keys | join(",")' "$labels_descriptor"
  )"

  echo "$(make_label_filter "$label_csv")"
}

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

function check_labels_descriptor() {
  check_labels_descriptor_schema
  check_labels_descriptor_has_predefined_labels
}

function get_labels_from_descriptor() {
  jq '
    .individual + (
      .group |
      [.[] | .colour as $colour | .labels | map_values(.colour = $colour)] |
      add
    )
  ' "$labels_descriptor"
}
