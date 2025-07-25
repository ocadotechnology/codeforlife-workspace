#!/bin/bash

source .github/scripts/general.sh

comment_path_prefix='.github/comments/'

function make_comment() {
  local body_file="$1"
  local substitutions="$2"

  if [[ ! "$body_file" =~ ^$comment_path_prefix ]]; then
    body_file="${comment_path_prefix}${body_file}"
  fi

  local body="$(cat "$body_file")"

  while IFS= read -r substitution; do
    substitution=$(trim_spaces "$substitution")
    if [ -z "$substitution" ]; then continue; fi

    local key="${substitution%=*}"
    local value="${substitution#*=}"

    body="$(echo "$body" | sed 's/{{ *'"$key"' *}}/'"$value"'/g')"
  done <<<"$substitutions"

  echo "$body"
}
