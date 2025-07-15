function eval_bool() {
  if [ "$1" = "true" ]; then return 0; else return 1; fi
}

function trim_spaces() {
  echo "$@" | sed --regexp-extended 's/^[[:space:]]*|[[:space:]]*$//g'
}

function download_workspace_file() {
  local branch="${branch:-"main"}"
  local path="$1"
  local save_to="${2:-"$path"}"

  # Make parent directories.
  mkdir -p "$(dirname "$save_to")"

  # Download file.
  wget https://raw.githubusercontent.com/ocadotechnology/codeforlife-workspace/refs/heads/$branch/$path \
    -O "$save_to"
}

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

  gh issue comment $ISSUE_NUMBER --repo=$REPO --body-file=$comment_path
}

function add_assignee() {
  gh api graphql -f query='
    mutation {
      addAssignee: addAssigneesToAssignable(input: {
        assignableId: "'$ISSUE_NODE_ID'"
        assigneeIds: ["'$USER_NODE_ID'"]
      }) {
        assignable { ... on Issue { id } }
      }
    }'
}

function remove_assignee() {
  gh api graphql -f query='
    mutation {
      removeAssignee: removeAssigneesFromAssignable(input: {
        assignableId: "'$ISSUE_NODE_ID'"
        assigneeIds: ["'$USER_NODE_ID'"]
      }) {
        assignable { ... on Issue { id } }
      }
    }'
}

function get_project_item_node_id() {
  gh api graphql -f query='
    query {
      repository(owner: "'"$REPO_OWNER"'", name: "'"$REPO_NAME"'") {
        issue(number: '"$ISSUE_NUMBER"') {
          projectItems(first: 1) {
            nodes {
              id
            }
          }
        }
      }
    }' | jq '.data.repository.issue.projectItems.nodes[0].id'
}

function add_label() {
  local label="$@"

  gh label create "$label" \
    --repo=$REPO \
    --force \
    --color="$color" \
    --description="$description"

  gh issue edit $ISSUE_NUMBER \
    --repo=$REPO \
    --add-label="$label"
}

function remove_label() {
  local label="$@"

  gh issue edit $ISSUE_NUMBER \
    --repo=$REPO \
    --remove-label="$label"
}

function has_label() {
  local label="$@"

  has_label=$(
    gh issue view $ISSUE_NUMBER \
      --repo=$REPO \
      --json=labels \
      --jq='.labels | map(.name) | contains(["'"$label"'"])'
  )

  return $(eval_bool "$has_label")
}

function get_status() {
  gh issue view $ISSUE_NUMBER \
    --repo=$REPO \
    --json=projectItems \
    --jq='.projectItems[0] | .status.optionId'
}

function set_status() {
  local name="$@"

  gh project item-edit "$project_number" \
    --id="$project_item_node_id" \
    --project-id="$project_id" \
    --field-id="$status_field_id" \
    --single-select-option-id="${status_option_ids["$name"]}"
}

status_field_id="PVTSSF_lADOAB_fG84AmfxNzgeYqqQ"
declare -A status_option_ids=(
  ["To Do"]="f75ad846"
  ["In Progress"]="47fc9ee4"
  ["Reviewing"]="cae0cfc1"
  ["Staging"]="b595bde1"
  ["Production"]="a0264d2c"
  ["Closed"]="98236657"
)

function status_is_one_of() {
  local no_status="${no_status:-1}"
  local option_name_csv="$@"

  local actual_option_id="$(get_status)"
  if [ -z "$actual_option_id" ]; then return $no_status; fi

  IFS=',' read -ra option_names <<<"$option_name_csv"

  for option_name in "${option_names[@]}"; do
    local option_id="${status_option_ids["$option_name"]}"
    if [ "$option_id" = "$actual_option_id" ]; then return 0; fi
  done

  return 1
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
  ["$link_pr_prompt_id"]="[:alnum:][:blank:]"
  ["$unlink_pr_prompt_id"]="[:alnum:][:blank:]"
)

# Define the POSIX regex pattern of each prompt.
# Used to check if the comment's body matches any of the prompts' pattern.
declare -A prompt_patterns=(
  ["$assign_me_prompt_id"]="^assign\ me$"
  ["$unassign_me_prompt_id"]="^unassign\ me$"
  ["$ready_for_review_prompt_id"]="^ready\ for\ review$"
  ["$requires_changes_prompt_id"]="^requires\ changes$"
  ["$link_pr_prompt_id"]="^link\ pr\ ([0-9]+)$"
  ["$unlink_pr_prompt_id"]="^unlink\ pr\ ([0-9]+)$"
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
  elif eval_bool "$ISSUE_HAS_MAX_ASSIGNEES"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$assign_me_prompt_id" \
      "max-assignees"
  else
    add_assignee

    if no_status=0 status_is_one_of "To Do"; then
      set_status "Reviewing"
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
    remove_assignee
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
  elif has_label "$ready_for_review_label"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$ready_for_review_prompt_id" \
      "already-labelled"
  elif status_is_reviewing; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$ready_for_review_prompt_id" \
      "already-reviewing"
  else
    color="#fbca04" \
      description="This issue is awaiting review by a CFL team member." \
      add_label "$ready_for_review_label"
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
  elif ! has_label "$ready_for_review_label"; then
    substitutions="contributor=@$USER_LOGIN" \
      download_and_write_prompt_comment \
      "$requires_changes_prompt_id" \
      "not-labelled"
  else
    remove_label "$ready_for_review_label"
  fi
}
function handle_link_pr_prompt() {
  echo "TODO: implement"
  exit 1
}
function handle_unlink_pr_prompt() {
  echo "TODO: implement"
  exit 1
}

project_id="PVT_kwDOAB_fG84AmfxN"
project_number="3"
project_item_node_id="$(get_project_item_node_id)"

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
    echo "Found matching prompt: \"$prompt_id\"."
    "handle_${prompt_id}_prompt"
    exit 0
  fi
done

echo "No matching prompt was found."
