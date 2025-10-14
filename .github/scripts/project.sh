#!/bin/bash

# https://github.com/orgs/ocadotechnology/projects/3
project_id="PVT_kwDOAB_fG84AmfxN"
project_number="3"
project_status_field_id="PVTSSF_lADOAB_fG84AmfxNzgeYqqQ"

declare -A project_status_option_ids=(
  ["To Do"]="f75ad846"
  ["In Progress"]="47fc9ee4"
  ["Ready For Review"]="13caf9e3"
  ["In Review"]="cae0cfc1"
  ["Staging"]="b595bde1"
  ["Production"]="a0264d2c"
  ["Closed"]="98236657"
)

function set_project_item_status() {
  local id="$1"
  local option_name="${@:2}"

  gh project item-edit "$project_number" \
    --id="$id" \
    --project-id="$project_id" \
    --field-id="$project_status_field_id" \
    --single-select-option-id="${project_status_option_ids["$option_name"]}"
}
