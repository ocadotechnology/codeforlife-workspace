#!/bin/bash

source .github/scripts/general.sh

labels_descriptor=".github/descriptors/labels.json"

cfl_bot_ignore_label=":robot:"

# Auto-collect all labels into an array if not already done so.
declare -a labels
if [ "${#labels[@]}" -eq 0 ]; then
  while read -r var_name; do
    if [[ "$var_name" =~ _label$ ]]; then labels+=("${!var_name}"); fi
  done < <(compgen -v)
fi

function make_label_filter() {
  local label_csv="$@"
  local label_count=0
  local label_filter="label:"
  local labels=()

  if [ -n "$exclude" ] && eval_bool "$exclude"; then
    label_filter="-$label_filter"
  fi

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
  local return_code=0
  local descriptor_labels="$(get_labels_from_descriptor)"
  local has_label=""

  for label in "${labels[@]}"; do
    has_label="$(echo "$descriptor_labels" | jq 'has("'"$label"'")')"
    if ! eval_bool "$has_label"; then
      echo_error "Label: \"$label\" is missing in \"$labels_descriptor\"."
      return_code=1
    fi
  done

  return $return_code
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
