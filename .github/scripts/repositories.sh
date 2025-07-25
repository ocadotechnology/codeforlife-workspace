#!/bin/bash

org_name="ocadotechnology"
repo_name_prefix='codeforlife-'

function normalize_repo_name() {
  local repo_name="$1"

  # TODO: fix repo name and delete this code block.
  if [ "$repo_name" = "rapid-router" ]; then
    echo "$repo_name"
    return 0
  fi

  if [[ ! "$repo_name" =~ ^$repo_name_prefix ]]; then
    repo_name="${repo_name_prefix}${repo_name}"
  fi

  echo "$repo_name"
}

function make_repo() {
  local repo_name="$1"
  repo_name="$(normalize_repo_name "$repo_name")"

  echo "$org_name/$repo_name"
}
