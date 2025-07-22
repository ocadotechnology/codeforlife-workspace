#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/github.sh

repo="$(make_repo "$ISSUE_REPO_NAME")"

# Download and read file containing body section from the workspace.
cfl_bot_issue_body_section_file=".github/comments/issue/body.md"
download_workspace_file "$cfl_bot_issue_body_section_file"
cfl_bot_issue_body_section="$(cat "$cfl_bot_issue_body_section_file")"

function edit_issue_body() {
  local issue_body="$@"

  gh issue edit "$ISSUE_NUMBER" --repo="$repo" --body="$issue_body"
}

function enforce_issue_body() {
  local issue_body="$@"

  if [ "$ISSUE_ASSIGNEES_LENGTH" -eq 0 ] ||
    [ -n "$(trim_spaces "$issue_body")" ]; then
    return 0
  fi

  local issue_assignee_login_csv="$(
    gh issue view "$ISSUE_NUMBER" \
      --repo="$repo" \
      --json=assignees \
      --jq='.assignees | map("@" + .login) | join(", ")'
  )"

  issue_comment="$(
    make_comment \
      "issue/enforce-body.md" \
      "assignees=$issue_assignee_login_csv"
  )"

  gh issue comment "$ISSUE_NUMBER" --repo="$repo" --body="$issue_comment"
}

function on_match_cfl_bot_body_section() {
  enforce_issue_body "${before_cfl_body_section}${after_cfl_body_section}"

  local issue_body="$before_cfl_body_section"
  issue_body+="$(make_cfl_body_section "$cfl_bot_issue_body_section")"
  issue_body+="$after_cfl_body_section"

  edit_issue_body "$issue_body"
}

function on_not_match_cfl_bot_body_section() {
  local issue_body="$@"

  enforce_issue_body "$issue_body"

  issue_body="$(
    body="$issue_body" \
      cfl_body_section="$cfl_bot_issue_body_section" \
      append_cfl_body_section
  )"

  edit_issue_body "$issue_body"
}

match_cfl_body_section \
  "on_match_cfl_bot_body_section" \
  "on_not_match_cfl_bot_body_section" \
  "$@"
