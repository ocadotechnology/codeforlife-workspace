# A helper utility to set outputs on the GitHub step.
function set_output() {
  local output="$1=$2"
  echo "Outputting to GitHub: $output"
  echo "$output" >>$GITHUB_OUTPUT
}

function extract_prompt() {
  # Normalize the comment's body:
  # 1. Remove any mention of "@cfl-bot".
  # 2. Remove all leading or trailing spaces.
  # 3. Substitute all 2+ recurring spaces with a single space.
  # 4. Replace all upper-case characters with lower-case.
  comment_body=$(
    echo "$1" |
      sed --regexp-extended '
      s/(^|\W)@cfl-bot($|\W)/\1\2/g;
      s/^[[:space:]]*|[[:space:]]*$//g;
      s/[[:space:]]{2,}/ /g
    ' |
      tr '[:upper:]' '[:lower:]'
  )

  # Define the character set of each prompt.
  # Used to remove all characters not in the set from the comment's body.
  declare -A prompt_char_sets=(
    ["$ASSIGN_ME_PROMPT_ID"]="[:alpha:][:blank:]"
    ["$UNASSIGN_ME_PROMPT_ID"]="[:alpha:][:blank:]"
    ["$READY_FOR_REVIEW_PROMPT_ID"]="[:alpha:][:blank:]"
    ["$REQUIRES_CHANGES_PROMPT_ID"]="[:alpha:][:blank:]"
    ["$LINK_PR_PROMPT_ID"]="[:alnum:][:blank:]"
    ["$UNLINK_PR_PROMPT_ID"]="[:alnum:][:blank:]"
  )

  # Define the POSIX regex pattern of each prompt.
  # Used to check if the comment's body matches any of the prompts' pattern.
  declare -A prompt_patterns=(
    ["$ASSIGN_ME_PROMPT_ID"]="^assign me$"
    ["$UNASSIGN_ME_PROMPT_ID"]="^unassign me$"
    ["$READY_FOR_REVIEW_PROMPT_ID"]="^ready for review$"
    ["$REQUIRES_CHANGES_PROMPT_ID"]="^requires changes$"
    ["$LINK_PR_PROMPT_ID"]="^link pr ([0-9]+)$"
    ["$UNLINK_PR_PROMPT_ID"]="^unlink pr ([0-9]+)$"
  )

  # Define a CSV of group names for each POSIX regex pattern that contains a group.
  # Used to set outputs on the GitHub step.
  declare -A prompt_patterns_group_name_csv=(
    ["$LINK_PR_PROMPT_ID"]="pr-number"
    ["$UNLINK_PR_PROMPT_ID"]="pr-number"
  )

  # The name of the output that identifies a prompt.
  prompt_id_key="id"

  for prompt_id in "${!prompt_char_sets[@]}"; do
    prompt_char_set="${prompt_char_sets[$prompt_id]}"
    prompt_pattern="${prompt_patterns[$prompt_id]}"

    # Remove all characters not in the set from the comment's body.
    comment_body_char_set=$(echo "$comment_body" | tr -dc "$prompt_char_set")

    # Check if the comment's body matches the prompt's pattern.
    if [[ "$comment_body_charset" =~ $prompt_pattern ]]; then
      # Output the matching prompt.
      set_output "$prompt_id_key" "$prompt_id"

      prompt_pattern_group_name_csv="${prompt_patterns_group_name_csv[$prompt_id]}"

      # Check if a group-name CSV was provided for the pattern.
      if [ -n "$prompt_pattern_group_name_csv" ]; then
        # Convert the CSV to an array.
        IFS=',' read -r -a prompt_pattern_group_names <<<"$prompt_pattern_group_name_csv"

        for i in "${!prompt_pattern_group_names[@]}"; do
          prompt_pattern_group_name="${prompt_pattern_group_names[$i]}"

          # Output the group.
          ((i++))
          set_output "$prompt_pattern_group_name" "${BASH_REMATCH[$i]}"
        done
      fi

      # Stop processing.
      exit 0
    fi
  done

  # Output that no matching prompt was found.
  set_output "$prompt_id_key" ""
}

# Call function by name and pass the remaining arguments.
if [ $# -gt 0 ]; then $1 ${@:2}; fi
