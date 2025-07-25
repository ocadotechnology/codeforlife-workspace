#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/github.sh

# ------------------------------------------------------------------------------
# Utility Functions.
# ------------------------------------------------------------------------------

function edit_issue_body() {
  local issue_number="$1"
  local issue_repo="$2"
  local issue_body="${@:3}"

  gh issue edit "$issue_number" --repo="$issue_repo" --body="$issue_body"
}

function enforce_issue_body() {
  local issue_number="$1"
  local issue_repo="$2"
  local issue_labels="$3"
  local issue_body="${@:4}"

  if [ -n "$(trim_spaces "$issue_body")" ]; then return 0; fi

  # TODO: select appropriate github team based on task-type label.
  local team="$full_team"

  local issue_comment_body="$(
    make_comment "issue/enforce-body.md" "team=@$org_name\/$team"
  )"

  all_outputs=$(
    gh issue comment "$issue_number" \
      --repo="$issue_repo" \
      --body="$issue_comment_body" \
      2>&1
  )

  if [ $? -eq 0 ]; then
    echo "Wrote comment: $all_outputs"
  else
    echo_warning "$all_outputs"
  fi
}

function get_non_cfl_bot_issue_body_section() {
  echo "${before_cfl_bot_body_section}${after_cfl_bot_body_section}"
}

function process_issue() {
  local issue_body="$@"

  match_cfl_bot_body_section \
    "on_match_cfl_bot_body_section" \
    "on_not_match_cfl_bot_body_section" \
    "$issue_body"
}

# ------------------------------------------------------------------------------
# Event handlers.
# Must follow the naming convention "handle_{event_name}_event".
# ------------------------------------------------------------------------------

function handle_issues_event() {
  local issue_body="$@"

  local issue_repo="$(make_repo "$ISSUE_REPO_NAME")"

  # Download and read file containing body section from the workspace.
  local cfl_bot_issue_body_section="$(cat ".github/comments/issue/body.md")"

  function _enforce_issue_body() {
    local issue_body="$@"

    local issue_labels="$(
      gh issue view "$ISSUE_NUMBER" \
        --repo="$issue_repo" \
        --json=labels |
        jq -c '.labels'
    )"

    enforce_issue_body \
      "$ISSUE_NUMBER" \
      "$issue_repo" \
      "$issue_labels" \
      "$issue_body"
  }

  function on_match_cfl_bot_body_section() {
    _enforce_issue_body "$(get_non_cfl_bot_issue_body_section)"

    local issue_body="$before_cfl_bot_body_section"
    issue_body+="$(make_cfl_bot_body_section "$cfl_bot_issue_body_section")"
    issue_body+="$after_cfl_bot_body_section"

    edit_issue_body "$ISSUE_NUMBER" "$issue_repo" "$issue_body"
  }

  function on_not_match_cfl_bot_body_section() {
    local issue_body="$@"

    _enforce_issue_body "$issue_body"

    issue_body="$(
      body="$issue_body" \
        cfl_bot_body_section="$cfl_bot_issue_body_section" \
        append_cfl_bot_body_section
    )"

    edit_issue_body "$ISSUE_NUMBER" "$issue_repo" "$issue_body"
  }

  process_issue "$issue_body"
}

function handle_schedule_event() {
  function process_repo() {
    local repo_name="$1"

    echo_h1 "$repo_name"

    local issue_repo="$(make_repo "$repo_name")"

    # TODO: dynamically get labels from json file.
    local task_type_labels="\"dev\""

    local issues=$(
      gh issue list \
        --repo="$issue_repo" \
        --limit=10000 \
        --search="is:open label:$task_type_labels $cfl_bot_ignore_label_filter" \
        --json=body,number,labels
    )

    echo "$issues" | jq -c '.[]' | while read -r issue; do
      issue_body=$(echo "$issue" | jq -r '.body')
      issue_number=$(echo "$issue" | jq -r '.number')
      issue_labels=$(echo "$issue" | jq -c '.labels')

      echo_info "Issue: #$issue_number"

      function _enforce_issue_body() {
        local issue_body="$@"

        enforce_issue_body \
          "$issue_number" \
          "$issue_repo" \
          "$issue_labels" \
          "$issue_body"
      }

      function on_match_cfl_bot_body_section() {
        _enforce_issue_body "$(get_non_cfl_bot_issue_body_section)"
      }

      function on_not_match_cfl_bot_body_section() {
        _enforce_issue_body "$issue_body"
      }

      process_issue "$issue_body"
    done
  }

  process_repo "$ISSUE_REPO_NAME"

  process_workspace_submodules "process_repo"
}

function handle_workflow_dispatch_event() { handle_schedule_event; }

# ------------------------------------------------------------------------------
# Entrypoint.
# ------------------------------------------------------------------------------

handle_event "$@"
