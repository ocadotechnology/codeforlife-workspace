#!/bin/bash

set -e

source .github/scripts/general.sh
source .github/scripts/github.sh

function download_and_write_prompt_comment() {
  local substitutions="$substitutions"
  local prompt_id="$1"
  local comment_md="$2"

  prompt_id="$(echo "$prompt_id" | sed 's/_/-/g')"

  local comment_path=".github/comments/issue/prompts/$prompt_id/$comment_md.md"

  download_workspace_file "$comment_path"

  # Write substitution to file.
  echo "$substitutions" | while IFS= read -r line; do
    IFS=',' read -ra pairs <<<"$line"

    for pair in "${pairs[@]}"; do
      pair=$(trim_spaces "$pair")
      if [ -z "$pair" ]; then continue; fi

      local key="${pair%=*}"
      local value="${pair#*=}"

      sed --in-place 's/{{ *'$key' *}}/'$value'/g' $comment_path
    done
  done

  comment_on_issue "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" "$comment_path"
}

# Labels.
ready_for_review_label="ready for review"

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

# Prompt handlers.
# Must follow the naming convention "handle_{prompt_id}_prompt".
function handle_assign_me_prompt() {
  if ! eval_bool "$ISSUE_IS_OPEN"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$assign_me_prompt_id" \
      "closed-state"
  elif eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$assign_me_prompt_id" \
      "already-assigned"
  elif [ "$ISSUE_ASSIGNEES_LENGTH" -ge 5 ]; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$assign_me_prompt_id" \
      "max-assignees"
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
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$unassign_me_prompt_id" \
      "not-assigned"
  else
    remove_assignee "$ISSUE_NODE_ID" "$USER_NODE_ID"
  fi
}
function handle_ready_for_review_prompt() {
  if ! eval_bool "$ISSUE_IS_OPEN"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$ready_for_review_prompt_id" \
      "closed-state"
  elif ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$ready_for_review_prompt_id" \
      "not-assigned"
  elif issue_has_label "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$ready_for_review_label"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$ready_for_review_prompt_id" \
      "already-labelled"
  elif issue_status_is_one_of "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "Reviewing"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$ready_for_review_prompt_id" \
      "already-reviewing"
  else
    color="#fbca04" \
      description="This issue is awaiting review by a CFL team member." \
      add_issue_label "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "$ready_for_review_label"
  fi
}
function handle_requires_changes_prompt() {
  if ! eval_bool "$ISSUE_IS_OPEN"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$requires_changes_prompt_id" \
      "closed-state"
  elif ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$requires_changes_prompt_id" \
      "not-assigned"
  elif ! issue_has_label "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$ready_for_review_label"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$requires_changes_prompt_id" \
      "not-labelled"
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
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$link_pr_prompt_id" \
      "closed-state"
  elif ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$link_pr_prompt_id" \
      "not-assigned"
  elif issue_has_pr_link \
    "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$pr_number" "$pr_repo_name"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$link_pr_prompt_id" \
      "already-linked"
  elif ! pr_exists "$pr_number" "$pr_repo_name"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$link_pr_prompt_id" \
      "not-exists"
  elif ! is_pr_author "$pr_number" "$pr_repo_name" "$USER_LOGIN"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$link_pr_prompt_id" \
      "not-author"
  else
    link_pr_to_issue \
      "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "$pr_number" "$pr_repo_name"

    substitutions="
    contributor=@$USER_LOGIN
    repo=$org_name\/$(normalize_repo_name "$pr_repo_name")
    pr_number=$pr_number" \
      download_and_write_prompt_comment \
      "$link_pr_prompt_id" \
      "success"
  fi
}
function handle_unlink_pr_prompt() {
  local pr_number="${BASH_REMATCH[1]}"
  local pr_repo_name="${BASH_REMATCH[2]}"

  if [ -z "$pr_repo_name" ]; then pr_repo_name="$ISSUE_REPO_NAME"; fi

  if ! eval_bool "$ISSUE_HAS_COMMENTER_ASSIGNED"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$unlink_pr_prompt_id" \
      "not-assigned"
  elif ! issue_has_pr_link \
    "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
    "$pr_number" "$pr_repo_name"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$unlink_pr_prompt_id" \
      "not-linked"
  elif ! is_pr_author "$pr_number" "$pr_repo_name" "$USER_LOGIN"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$unlink_pr_prompt_id" \
      "not-author"
  else
    unlink_pr_from_issue \
      "$ISSUE_NUMBER" "$ISSUE_REPO_NAME" \
      "$pr_number" "$pr_repo_name"

    substitutions="
    contributor=@$USER_LOGIN
    repo=$org_name\/$(normalize_repo_name "$pr_repo_name")
    pr_number=$pr_number" \
      download_and_write_prompt_comment \
      "$unlink_pr_prompt_id" \
      "success"
  fi
}

# Normalize the comment's body:
# 1. Remove any mention of "@cfl-bot".
# 2. Remove all leading or trailing spaces.
# 3. Substitute all 2+ recurring spaces with a single space.
# 4. Replace all upper-case characters with lower-case.
comment_body=$(
  trim_spaces "$@" |
    sed --regexp-extended '
      s/(^|\W)@cfl-bot($|\W)/\1\2/g;
      s/[[:space:]]{2,}/ /g
    ' |
    tr '[:upper:]' '[:lower:]'
)

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
