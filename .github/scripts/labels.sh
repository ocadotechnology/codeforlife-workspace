#!/bin/bash

source .github/scripts/general.sh

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
    jq -r '.labels.group.'"$group"'.labels | keys | join(",")' \
      .github/descriptors/repository.json
  )"

  echo "$(make_label_filter "$label_csv")"
}
