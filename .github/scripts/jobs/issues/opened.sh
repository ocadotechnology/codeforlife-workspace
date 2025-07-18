#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/github.sh

# Download and read file containing body section from the workspace.
issue_opened_body_section_file=".github/comments/issue/was-opened.md"
download_workspace_file "$issue_opened_body_section_file"
issue_opened_body_section="$(cat "$issue_opened_body_section_file")"

# Match the cfl-bot section in the issue's body.
# If it's matched, overwrite. Else, append it.
function overwrite() {
  local issue_body="$before_cfl_body_section"
  issue_body+="$(make_cfl_body_section "$issue_opened_body_section")"
  issue_body+="$after_cfl_body_section"

  edit_issue "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" --body="$issue_body"
}
function append() {
  local issue_body="$(
    body="$@" \
      cfl_body_section="$issue_opened_body_section" \
      append_cfl_body_section
  )"

  edit_issue "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" --body="$issue_body"
}
match_cfl_body_section "overwrite" "append" "$@"
