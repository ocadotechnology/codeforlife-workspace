#!/bin/bash

source .github/scripts/general.sh
source .github/scripts/repositories.sh
source .github/scripts/project.sh

function add_issue_label() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local label="${@:3}"

  gh label create "$label" \
    --repo="$(make_repo "$issue_repo_name")" \
    --force \
    --color="$color" \
    --description="$description"

  gh issue edit "$issue_number" \
    --repo="$(make_repo "$issue_repo_name")" \
    --add-label="$label"
}

function remove_issue_label() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local label="${@:3}"

  gh issue edit "$issue_number" \
    --repo="$(make_repo "$issue_repo_name")" \
    --remove-label="$label"
}

function issue_has_label() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local label="${@:3}"

  has_label=$(
    gh issue view "$issue_number" \
      --repo="$(make_repo "$issue_repo_name")" \
      --json=labels \
      --jq='.labels | map(.name) | contains(["'"$label"'"])'
  )

  return $(eval_bool "$has_label")
}

function get_issue_project_item_id() {
  local issue_repo_name="$1"
  local issue_number="$2"

  gh api graphql -f query='
    query {
      repository(owner: "'"$org_name"'", name: "'"$issue_repo_name"'") {
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

function issue_status_is_one_of() {
  local no_status="${no_status:-1}"
  local issue_number="$1"
  local issue_repo_name="$2"
  local option_name_csv="${@:3}"

  local actual_option_id="$(
    gh issue view "$issue_number" \
      --repo="$(make_repo "$issue_repo_name")" \
      --json=projectItems \
      --jq='.projectItems[0] | .status.optionId'
  )"
  if [ -z "$actual_option_id" ]; then return $no_status; fi

  IFS=',' read -ra option_names <<<"$option_name_csv"

  for option_name in "${option_names[@]}"; do
    local option_id="${project_status_option_ids["$option_name"]}"
    if [ "$option_id" = "$actual_option_id" ]; then return 0; fi
  done

  return 1
}
