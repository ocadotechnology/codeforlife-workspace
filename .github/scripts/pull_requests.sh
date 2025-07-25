#!/bin/bash

source .github/scripts/repositories.sh
source .github/scripts/bodies.sh

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
    local pr_body="$before_cfl_bot_body_section"
    pr_body+="$(make_cfl_bot_body_section "$cfl_bot_body_section
$issue_link")"
    pr_body+="$after_cfl_bot_body_section"

    gh pr edit "$pr_number" --repo="$pr_repo" --body="$pr_body"
  }

  function _link_pr_to_issue__no_match() {
    local pr_body="$@"
    pr_body="$(
      body="$pr_body" cfl_bot_body_section="$issue_link" \
        append_cfl_bot_body_section
    )"

    gh pr edit "$pr_number" --repo="$pr_repo" --body="$pr_body"
  }

  match_cfl_bot_body_section \
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

  return $(eval_bool "$is_pr_author")
}

function pr_exists() {
  local number="$1"
  local repo_name="$2"

  gh pr view "$number" --repo="$(make_repo "$repo_name")" >/dev/null 2>&1

  if [ $? -eq 0 ]; then return 0; else return 1; fi
}
