#!/bin/bash

source .github/scripts/general.sh

project_id="PVT_kwDOAB_fG84AmfxN"
project_number="3"
project_status_field_id="PVTSSF_lADOAB_fG84AmfxNzgeYqqQ"

declare -A project_status_option_ids=(
  ["To Do"]="f75ad846"
  ["In Progress"]="47fc9ee4"
  ["Reviewing"]="cae0cfc1"
  ["Staging"]="b595bde1"
  ["Production"]="a0264d2c"
  ["Closed"]="98236657"
)

function _format_assignee_ids() {
  echo "$@" | sed 's/ /","/g; s/^/"/; s/$/"/'
}

function add_assignee() {
  local assignable_id="$1"
  local assignee_ids="${@:2}"

  assignee_ids="$(_format_assignee_ids "$assignee_ids")"

  gh api graphql -f query='
    mutation {
      addAssignee: addAssigneesToAssignable(input: {
        assignableId: "'$assignable_id'"
        assigneeIds: ['$assignee_ids']
      }) {
        assignable { ... on Issue { id } }
      }
    }'
}

function remove_assignee() {
  local assignable_id="$1"
  local assignee_ids="${@:2}"

  assignee_ids="$(_format_assignee_ids "$assignee_ids")"

  gh api graphql -f query='
    mutation {
      removeAssignee: removeAssigneesFromAssignable(input: {
        assignableId: "'$assignable_id'"
        assigneeIds: ['$assignee_ids']
      }) {
        assignable { ... on Issue { id } }
      }
    }'
}

function create_label() {
  local repo="$1"
  local label="${@:2}"

  gh label create "$label" \
    --repo=$repo \
    --force \
    --color="$color" \
    --description="$description"
}

function add_issue_label() {
  local number="$1"
  local repo="$2"
  local label="${@:3}"

  create_label "$repo" "$label"

  gh issue edit "$number" \
    --repo=$repo \
    --add-label="$label"
}

function remove_issue_label() {
  local number="$1"
  local repo="$2"
  local label="${@:3}"

  gh issue edit "$number" \
    --repo=$repo \
    --remove-label="$label"
}

function issue_has_label() {
  local number="$1"
  local repo="$2"
  local label="${@:3}"

  has_label=$(
    gh issue view "$number" \
      --repo=$repo \
      --json=labels \
      --jq='.labels | map(.name) | contains(["'"$label"'"])'
  )

  return $(eval_bool "$has_label")
}

function get_issue_status() {
  local number="$1"
  local repo="$2"

  gh issue view "$number" \
    --repo=$repo \
    --json=projectItems \
    --jq='.projectItems[0] | .status.optionId'
}

function issue_status_is_one_of() {
  local no_status="${no_status:-1}"
  local number="$1"
  local repo="$2"
  local option_name_csv="${@:3}"

  local actual_option_id="$(get_issue_status "$number" "$repo")"
  if [ -z "$actual_option_id" ]; then return $no_status; fi

  IFS=',' read -ra option_names <<<"$option_name_csv"

  for option_name in "${option_names[@]}"; do
    local option_id="${project_status_option_ids["$option_name"]}"
    if [ "$option_id" = "$actual_option_id" ]; then return 0; fi
  done

  return 1
}

function set_project_status() {
  local id="$1"
  local option_name="${@:2}"

  gh project item-edit "$project_number" \
    --id="$id" \
    --project-id="$project_id" \
    --field-id="$project_status_field_id" \
    --single-select-option-id="${project_status_option_ids["$option_name"]}"
}

function get_issue_project_item_id() {
  local repo_owner="$1"
  local repo_name="$2"
  local issue_number="$3"

  gh api graphql -f query='
    query {
      repository(owner: "'"$repo_owner"'", name: "'"$repo_name"'") {
        issue(number: '"$issue_number"') {
          projectItems(first: 1) {
            nodes {
              id
            }
          }
        }
      }
    }' | jq -r '.data.repository.issue.projectItems.nodes[0].id'
}
