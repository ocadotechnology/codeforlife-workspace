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
  local issue_assignees="$3"
  local issue_body="${@:4}"

  if [ -n "$(trim_spaces "$issue_body")" ]; then return 0; fi

  local issue_comment_body="$(
    make_comment "issue/enforce-body.md" "assignees=$(
      echo "$issue_assignees" | jq 'map("@" + .login) | join(", ")'
    )"
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
  echo "${before_cfl_body_section}${after_cfl_body_section}"
}

function process_issue() {
  local issue_body="$@"

  match_cfl_body_section \
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
  local cfl_bot_issue_body_section_file=".github/comments/issue/body.md"
  download_workspace_file "$cfl_bot_issue_body_section_file"
  local cfl_bot_issue_body_section="$(cat "$cfl_bot_issue_body_section_file")"

  function _enforce_issue_body() {
    local issue_body="$@"

    local issue_assignees="$(
      gh issue view "$ISSUE_NUMBER" \
        --repo="$issue_repo" \
        --json=assignees |
        jq -c '.assignees'
    )"

    if [ "$ISSUE_ASSIGNEES_LENGTH" -ge 1 ]; then
      enforce_issue_body \
        "$ISSUE_NUMBER" \
        "$issue_repo" \
        "$issue_assignees" \
        "$issue_body"
    fi
  }

  function on_match_cfl_bot_body_section() {
    _enforce_issue_body "$(get_non_cfl_bot_issue_body_section)"

    local issue_body="$before_cfl_body_section"
    issue_body+="$(make_cfl_body_section "$cfl_bot_issue_body_section")"
    issue_body+="$after_cfl_body_section"

    edit_issue_body "$ISSUE_NUMBER" "$issue_repo" "$issue_body"
  }

  function on_not_match_cfl_bot_body_section() {
    local issue_body="$@"

    _enforce_issue_body "$issue_body"

    issue_body="$(
      body="$issue_body" \
        cfl_body_section="$cfl_bot_issue_body_section" \
        append_cfl_body_section
    )"

    edit_issue_body "$ISSUE_NUMBER" "$issue_repo" "$issue_body"
  }

  process_issue "$issue_body"
}

function handle_schedule_event() {
  function process_repo() {
    local submodule_name="$1"

    local issue_repo="$(make_repo "$submodule_name")"

    local issues=$(
      gh issue list \
        --repo="$issue_repo" \
        --limit=10000 \
        --search="is:open has:assignee -label:\"bot ignore\"" \
        --json=body,number,assignees \
        --jq="map(select(.assignees | length > 0))"
    )

    echo "$issues" | jq -c '.[]' | while read -r issue; do
      issue_body=$(echo "$issue" | jq -r '.body')
      issue_number=$(echo "$issue" | jq -r '.number')
      issue_assignees=$(echo "$issue" | jq -r '.assignees')

      echo_info "Issue: #$issue_number"

      function _enforce_issue_body() {
        local issue_body="$@"

        enforce_issue_body \
          "$issue_number" \
          "$issue_repo" \
          "$issue_assignees" \
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

  process_workspace_submodules "process_repo"
}

function handle_workflow_dispatch_event() { handle_schedule_event; }

# ------------------------------------------------------------------------------
# Entrypoint.
# ------------------------------------------------------------------------------

if [ -z "$EVENT_NAME" ]; then
  exit=1 echo_error "Event name not defined."
else
  "handle_${EVENT_NAME}_event" "$@"
fi
