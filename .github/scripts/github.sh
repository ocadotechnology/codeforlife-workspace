#!/bin/bash

source .github/scripts/general.sh

org_name="ocadotechnology"
repo_name_prefix='codeforlife-'

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

cfl_body_section_name='cfl-bot'
cfl_body_section_start='<!-- '$cfl_body_section_name':start -->'
cfl_body_section_end='<!-- '$cfl_body_section_name':end -->'

function download_workspace_file() {
  local branch="${branch:-"main"}"
  local path="$1"
  local save_to="${2:-"$path"}"

  # Make parent directories.
  mkdir -p "$(dirname "$save_to")"

  # Download file.
  wget https://raw.githubusercontent.com/$org_name/codeforlife-workspace/refs/heads/$branch/$path \
    -O "$save_to"
}

function normalize_repo_name() {
  local repo_name="$1"

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

function make_cfl_body_section() {
  local cfl_body_section="$@"

  echo "${cfl_body_section_start}${cfl_body_section}${cfl_body_section_end}"
}

function append_cfl_body_section() {
  local cfl_body_section="$(make_cfl_body_section "
$cfl_body_section
")"

  if [ -z "$body" ]; then
    echo "$cfl_body_section"
  else
    echo "$body

$cfl_body_section"
  fi
}

function match_cfl_body_section() {
  local match_callback="$1"
  local no_match_callback="$2"
  local body="${@:3}"

  local pattern="(.*)"
  pattern+="$cfl_body_section_start"
  pattern+="(.*)"
  pattern+="$cfl_body_section_end"
  pattern+="(.*)"

  if [[ "$body" =~ $pattern ]]; then
    before_cfl_body_section="${BASH_REMATCH[1]}" \
      cfl_body_section="${BASH_REMATCH[2]}" \
      after_cfl_body_section="${BASH_REMATCH[3]}" \
      $match_callback
  else
    $no_match_callback "$body"
  fi
}

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
  local repo_name="$1"
  local label="${@:2}"

  gh label create "$label" \
    --repo="$(make_repo "$repo_name")" \
    --force \
    --color="$color" \
    --description="$description"
}

function add_issue_label() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local label="${@:3}"

  create_label "$issue_repo_name" "$label"

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

function issue_has_pr_link() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local pr_number="$3"
  local pr_repo_name="$4"

  local issue_repo="$(make_repo "$issue_repo_name")"
  local pr_repo="$(make_repo "$pr_repo_name")"

  local pr_body="$(
    gh pr view "$pr_number" \
      --repo="$pr_repo" \
      --json="body" \
      --jq=".body"
  )"

  if [[ "$pr_body" =~ Resolves\ $issue_repo#$issue_number ]]; then
    return 0
  fi

  return 1
}

function link_pr_to_issue() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local pr_number="$3"
  local pr_repo_name="$4"

  local issue_repo="$(make_repo "$issue_repo_name")"
  local pr_repo="$(make_repo "$pr_repo_name")"

  local issue_link="Resolves $issue_repo#$issue_number"

  local pr_body="$(
    gh pr view "$pr_number" \
      --repo="$pr_repo" \
      --json="body" \
      --jq=".body"
  )"

  function _link_pr_to_issue__match() {
    local pr_body="$before_cfl_body_section"
    pr_body+="$(make_cfl_body_section "$cfl_body_section
$issue_link
")"
    pr_body+="$after_cfl_body_section"

    gh pr edit "$pr_number" --repo="$pr_repo" --body="$pr_body"
  }

  function _link_pr_to_issue__no_match() {
    local pr_body="$@"
    pr_body="$(
      body="$pr_body" cfl_body_section="$issue_link" append_cfl_body_section
    )"

    gh pr edit "$pr_number" --repo="$pr_repo" --body="$pr_body"
  }

  match_cfl_body_section \
    "_link_pr_to_issue__match" \
    "_link_pr_to_issue__no_match" \
    "$pr_body"
}

function unlink_pr_from_issue() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local pr_number="$3"
  local pr_repo_name="$4"

  local pr_repo="$(make_repo "$pr_repo_name")"

  local pr_body="$(
    gh pr view "$pr_number" \
      --repo="$pr_repo" \
      --json="body" \
      --jq=".body"
  )"
  pr_body="$(
    echo "$pr_body" |
      sed 's/Resolves '$org_name'\/'$issue_repo_name'#'$issue_number'//g'
  )"

  gh pr edit "$pr_number" --repo="$pr_repo" --body="$pr_body"
}

function comment_on_issue() {
  local issue_number="$1"
  local issue_repo_name="$2"
  local body_file="$3"

  gh issue comment "$issue_number" \
    --repo="$(make_repo "$issue_repo_name")" \
    --body-file="$body_file"
}

function edit_issue() {
  local number="$1"
  local repo_name="$2"
  local args="${@:3}"

  gh issue edit "$number" \
    --repo="$(make_repo "$repo_name")" \
    "$args"
}

function is_pr_author() {
  local number="$1"
  local repo_name="$2"
  local author_login="$3"

  local is_pr_author="$(
    gh pr view "$number" \
      --repo="$(make_repo "$repo_name")" \
      --json=author \
      --jq='.author.login == "'"$author_login"'"'
  )"

  return $(eval_bool "$has_label")
}
