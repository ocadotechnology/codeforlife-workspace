#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/assignees.sh
source .github/scripts/issues.sh
source .github/scripts/pull_requests.sh
source .github/scripts/labels.sh
source .github/scripts/project.sh
source .github/scripts/repositories.sh
source .github/scripts/templates.sh
source .github/scripts/workspace.sh

# ------------------------------------------------------------------------------
# Prompt registry.
# ------------------------------------------------------------------------------

# Prompt IDs.
# Must be written in snake case and end with "_prompt_id".
assign_me_prompt_id="assign_me"
unassign_me_prompt_id="unassign_me"
ready_for_review_prompt_id="ready_for_review"
requires_changes_prompt_id="requires_changes"
link_pr_prompt_id="link_pr"
unlink_pr_prompt_id="unlink_pr"

# Define the character set of each prompt.
# Used to remove all characters not in the set from the comment's body.
declare -A prompt_char_sets=(
  ["$assign_me_prompt_id"]="[:alpha:][:blank:]"
  ["$unassign_me_prompt_id"]="[:alpha:][:blank:]"
  ["$ready_for_review_prompt_id"]="[:alpha:][:blank:]"
  ["$requires_changes_prompt_id"]="[:alpha:][:blank:]"
  ["$link_pr_prompt_id"]="[:alnum:][:blank:][=-=]"
  ["$unlink_pr_prompt_id"]="[:alnum:][:blank:][=-=]"
)

# Define the POSIX regex pattern of each prompt.
# Used to check if the comment's body matches any of the prompts' pattern.
declare -A prompt_patterns=(
  ["$assign_me_prompt_id"]='^assign me$'
  ["$unassign_me_prompt_id"]='^unassign me$'
  ["$ready_for_review_prompt_id"]='^ready for review$'
  ["$requires_changes_prompt_id"]='^requires changes$'
  ["$link_pr_prompt_id"]='^link pr ([0-9]+) ?([a-z-]*)$'
  ["$unlink_pr_prompt_id"]='^unlink pr ([0-9]+) ?([a-z-]*)$'
)

# Auto-collect all prompt ids into an array.
declare -a prompt_ids
while read -r var_name; do
  if [[ ! "$var_name" =~ _prompt_id$ ]]; then continue; fi

  prompt_id="${!var_name}"

  prompt_char_set="${prompt_char_sets[$prompt_id]}"
  if [ -z "$prompt_char_set" ]; then
    echo "A character set was not defined for prompt ID: \"$prompt_id\"."
    exit 1
  fi

  prompt_pattern="${prompt_patterns[$prompt_id]}"
  if [ -z "$prompt_pattern" ]; then
    echo "A pattern was not defined for prompt ID: \"$prompt_id\"."
    exit 1
  fi

  prompt_ids+=("$prompt_id")
done < <(compgen -v)

# ------------------------------------------------------------------------------
# Prompt handlers.
# Must follow the naming convention "handle_{prompt_id}_prompt".
# ------------------------------------------------------------------------------

function handle_assign_me_prompt() {
  if ! eval_bool "$ISSUE_IS_OPEN"; then
    comment_on_issue "closed-state" \
      "contributor=@$USER_LOGIN"
  elif eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    comment_on_issue "already-assigned" \
      "contributor=@$USER_LOGIN"
  elif [ "$ISSUE_ASSIGNEES_LENGTH" -ge 5 ]; then
    comment_on_issue "max-assignees" \
      "contributor=@$USER_LOGIN"
  else
    add_assignee "$ISSUE_NODE_ID" "$USER_NODE_ID"

    if no_status=0 issue_status_is_one_of "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "To Do"; then
      issue_project_item_id="$(
        get_issue_project_item_id "$ISSUE_REPO_NAME" "$ISSUE_NUMBER"
      )"

      set_project_status "$issue_project_item_id" "In Progress"
    fi
  fi
}

function handle_unassign_me_prompt() {
  if ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    comment_on_issue "not-assigned" \
      "contributor=@$USER_LOGIN"
  else
    remove_assignee "$ISSUE_NODE_ID" "$USER_NODE_ID"
  fi
}

function handle_ready_for_review_prompt() {
  if ! eval_bool "$ISSUE_IS_OPEN"; then
    comment_on_issue "closed-state" \
      "contributor=@$USER_LOGIN"
  elif ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    comment_on_issue "not-assigned" \
      "contributor=@$USER_LOGIN"
  elif issue_has_label "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$ready_for_review_label"; then
    comment_on_issue "already-labelled" \
      "contributor=@$USER_LOGIN"
  elif issue_status_is_one_of "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "Reviewing"; then
    comment_on_issue "already-reviewing" \
      "contributor=@$USER_LOGIN"
  else
    color="#fbca04" \
      description="This issue is awaiting review by a CFL team member." \
      add_issue_label "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "$ready_for_review_label"
  fi
}

function handle_requires_changes_prompt() {
  if ! eval_bool "$ISSUE_IS_OPEN"; then
    comment_on_issue "closed-state" \
      "contributor=@$USER_LOGIN"
  elif ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    comment_on_issue "not-assigned" \
      "contributor=@$USER_LOGIN"
  elif ! issue_has_label "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$ready_for_review_label"; then
    comment_on_issue "not-labelled" \
      "contributor=@$USER_LOGIN"
  else
    remove_issue_label "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "$ready_for_review_label"
  fi
}

function handle_link_pr_prompt() {
  local pr_number="${BASH_REMATCH[1]}"
  local pr_repo_name="${BASH_REMATCH[2]}"

  if [ -z "$pr_repo_name" ]; then pr_repo_name="$ISSUE_REPO_NAME"; fi

  if ! eval_bool "$ISSUE_IS_OPEN"; then
    comment_on_issue "closed-state" \
      "contributor=@$USER_LOGIN"
  elif ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    comment_on_issue "not-assigned" \
      "contributor=@$USER_LOGIN"
  elif issue_has_pr_link \
    "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$pr_number" "$pr_repo_name"; then
    comment_on_issue "already-linked" \
      "contributor=@$USER_LOGIN"
  elif ! pr_exists "$pr_number" "$pr_repo_name"; then
    comment_on_issue "not-exists" \
      "contributor=@$USER_LOGIN"
  elif ! is_pr_author "$pr_number" "$pr_repo_name" "$USER_LOGIN"; then
    comment_on_issue "not-author" \
      "contributor=@$USER_LOGIN"
  else
    link_pr_to_issue \
      "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "$pr_number" "$pr_repo_name"

    comment_on_issue "success" \
      "contributor=@$USER_LOGIN
      repo=$org_name\/$(normalize_repo_name "$pr_repo_name")
      pr_number=$pr_number"
  fi
}

function handle_unlink_pr_prompt() {
  local pr_number="${BASH_REMATCH[1]}"
  local pr_repo_name="${BASH_REMATCH[2]}"

  if [ -z "$pr_repo_name" ]; then pr_repo_name="$ISSUE_REPO_NAME"; fi

  if ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    comment_on_issue "not-assigned" \
      "contributor=@$USER_LOGIN"
  elif ! issue_has_pr_link \
    "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$pr_number" "$pr_repo_name"; then
    comment_on_issue "not-linked" \
      "contributor=@$USER_LOGIN"
  elif ! is_pr_author "$pr_number" "$pr_repo_name" "$USER_LOGIN"; then
    comment_on_issue "not-author" \
      "contributor=@$USER_LOGIN"
  else
    unlink_pr_from_issue \
      "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "$pr_number" "$pr_repo_name"

    comment_on_issue "success" \
      "contributor=@$USER_LOGIN
      repo=$org_name\/$(normalize_repo_name "$pr_repo_name")
      pr_number=$pr_number"
  fi
}

# ------------------------------------------------------------------------------
# Script.
# ------------------------------------------------------------------------------

repo="$(make_repo "$ISSUE_REPO_NAME")"

# Utility to write a prompt's comment on an issue.
function comment_on_issue() {
  local comment_md="$1"
  local substitutions="$2"

  prompt_id="$(echo "$prompt_id" | sed 's/_/-/g')"

  local body="$(
    make_comment "issue/prompts/$prompt_id/$comment_md.md" "$substitutions"
  )"

  gh issue comment "$ISSUE_NUMBER" --repo="$repo" --body="$body"
}

comment_body="$(gh api repos/$repo/issues/comments/$COMMENT_ID --jq=.body)"
# Normalize the comment's body:
# 1. Remove any mention of "@cfl-bot".
# 2. Remove all leading or trailing spaces.
# 3. Substitute all 2+ recurring spaces with a single space.
# 4. Replace all upper-case characters with lower-case.
comment_body="$(
  trim_spaces "$comment_body" |
    sed --regexp-extended '
      s/(^|\W)@cfl-bot($|\W)/\1\2/g;
      s/[[:space:]]{2,}/ /g
    ' |
    tr '[:upper:]' '[:lower:]'
)"

for prompt_id in "${prompt_ids[@]}"; do
  prompt_char_set="${prompt_char_sets[$prompt_id]}"
  prompt_pattern="${prompt_patterns[$prompt_id]}"

  # Remove all characters not in the set from the comment's body.
  comment_body_char_set=$(echo "$comment_body" | tr -dc "$prompt_char_set")

  # Check if the comment's body matches the prompt's pattern.
  if [[ "$comment_body_char_set" =~ $prompt_pattern ]]; then
    echo_success "Found matching prompt: \"$prompt_id\"."
    "handle_${prompt_id}_prompt"
    exit 0
  fi
done

echo_info "No matching prompt was found."
