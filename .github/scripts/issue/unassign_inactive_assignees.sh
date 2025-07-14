repo="ocadotechnology/$1"
echo "-------------------------------------------------------------"
echo "Repository: $repo"

function timestamp_to_unix_epoch() {
  local timestamp="$1"
  if [ -z "$timestamp" ]; then
    echo "Error: No date provided."
    exit 1
  fi

  local unix_epoch=$(TZ="UTC" date --date="$timestamp" +%s)
  if [ -z "$unix_epoch" ]; then
    echo "Error: Invalid timestamp format for '$timestamp'."
    exit 2
  fi

  echo "$unix_epoch"
}

function get_latest_timestamp() {
  local timestamp_1="$1"
  local timestamp_2="$2"

  local unix_epoch_1="$(timestamp_to_unix_epoch "$timestamp_1")"
  local unix_epoch_2="$(timestamp_to_unix_epoch "$timestamp_2")"

  if [[ "$unix_epoch_1" -gt "$unix_epoch_2" ]]; then
    echo "$timestamp_1"
  elif [[ "$unix_epoch_2" -gt "$unix_epoch_1" ]]; then
    echo "$timestamp_2"
  else # "$unix_epoch_1" -eq "$unix_epoch_2"
    echo "$timestamp_1"
  fi
}

function is_ge_start_and_lt_end_days_old() {
  local timestamp="$1" # date
  local start_days=$2
  local end_days=$3

  local unix_epoch="$(timestamp_to_unix_epoch "$timestamp")"

  if [[ "$start_days" -eq 0 && "$end_days" -eq 0 ]]; then
    echo "Error: The start and end cannot both be unset."
    exit 2
  elif [[ 
    "$start_days" -ne 0 &&
    "$end_days" -ne 0 &&
    "$end_days" -gt "$start_days" ]] \
    ; then
    echo "Error: The end is greater than the start."
    exit 3
  fi

  local now=$(date +%s)

  if [[ 
    (
    "$start_days" -eq 0 ||
    "$unix_epoch" -ge $((now - (60 * 60 * 24 * start_days)))) &&
    (
    "$end_days" -eq 0 ||
    "$unix_epoch" -lt $((now - (60 * 60 * 24 * end_days)))) ]] \
    ; then return 0; else return 1; fi
}

function comment_on_issue() {
  local issue_number="$1"
  local comment_path="$2"

  local substitutions=''
  for substitution in "${@:3}"; do
    local key="${substitution%=*}"
    local value="${substitution#*=}"

    substitutions+='s/{{ *'$key' *}}/'$value'/g;'
  done

  all_outputs=$(
    gh issue comment $issue_number \
      --repo=$repo \
      --body="$(sed "$substitutions" "$comment_path")" \
      2>&1
  )

  if [ $? -eq 0 ]; then
    echo "    Wrote comment: $all_outputs"
  else
    echo "    $all_outputs"
    exit_code=1
  fi
}

issues=$(
  gh issue list \
    --repo=$repo \
    --limit=10000 \
    --search="is:open has:assignee -label:\"bot ignore\"" \
    --json=id,number,url,assignees \
    --jq="map(select(.assignees | length > 0))"
)

echo "$issues" | jq -c '.[]' | while read -r issue; do
  issue_id=$(echo "$issue" | jq -r '.id')
  issue_number=$(echo "$issue" | jq -r '.number')
  issue_assignees=$(echo "$issue" | jq -r '.assignees')

  echo "  Issue: #$issue_number"

  issue_comments=$(
    gh api "/repos/$repo/issues/$issue_number/comments" \
      --paginate \
      --header "Accept: application/vnd.github+json" \
      --jq="sort_by(.updated_at)"
  )

  issue_assigned_events=$(
    gh api "repos/$repo/issues/$issue_number/events" \
      --paginate \
      --jq='map(select(.event == "assigned")) | sort_by(.created_at)'
  )

  issue_assignees_to_remove=()

  while read -r issue_assignee; do
    issue_assignee_id=$(echo "$issue_assignee" | jq -r '.id')
    issue_assignee_login=$(echo "$issue_assignee" | jq -r '.login')

    if [ "$issue_assignee_login" = "cfl-bot" ]; then continue; fi

    issue_assignee_last_comment_updated_at=$(
      echo "$issue_comments" |
        jq -r '
          map(select(.user.node_id == "'$issue_assignee_id'")) |
          last |
          .updated_at'
    )

    issue_assignee_last_assigned_event_created_at=$(
      echo "$issue_assigned_events" | jq -r '
          map(select(.assignee.login == "'$issue_assignee_login'")) | 
          last | 
          .created_at'
    )

    if [ "$issue_assignee_last_comment_updated_at" = "null" ]; then
      issue_assignee_last_active_at="$issue_assignee_last_assigned_event_created_at"
    else
      issue_assignee_last_active_at=$(
        get_latest_timestamp \
          "$issue_assignee_last_comment_updated_at" \
          "$issue_assignee_last_assigned_event_created_at"
      )
    fi

    if is_ge_start_and_lt_end_days_old \
      "$issue_assignee_last_active_at" \
      8 7; then
      comment_on_issue $issue_number "$ONE_WEEK_MD" \
        "assignee=@$issue_assignee_login"
    elif is_ge_start_and_lt_end_days_old \
      "$issue_assignee_last_active_at" \
      15 14; then
      comment_on_issue $issue_number "$TWO_WEEKS_MD" \
        "assignee=@$issue_assignee_login"
    elif is_ge_start_and_lt_end_days_old \
      "$issue_assignee_last_active_at" \
      0 21; then
      comment_on_issue $issue_number "$THREE_WEEKS_MD" \
        "assignee=@$issue_assignee_login"

      issue_assignees_to_remove+=("$issue_assignee")
    fi
  done < <(echo "$issue_assignees" | jq -c '.[]')

  if [[ "${#issue_assignees_to_remove[@]}" -gt 0 ]]; then
    issue_assignees_to_remove="[$(
      IFS=,
      echo "${issue_assignees_to_remove[*]}"
    )]"

    echo "    Removing assignees: $(
      echo "$issue_assignees_to_remove" |
        jq -r 'map(.login) | join(", ")'
    )."

    issue_assignee_ids_to_remove=$(
      echo "$issue_assignees_to_remove" |
        jq -r 'map(.id | "\"" + . + "\"") | join(",")'
    )

    error_output=$(
      gh api graphql -f query='
        mutation {
          removeAssigneesFromAssignable(input: {
            assignableId: "'$issue_id'"
            assigneeIds: ['$issue_assignee_ids_to_remove']
          }) {
            assignable { ... on Issue { id } }
          }
        }' 2>&1 >/dev/null
    )

    if [ $? -ne 0 ]; then
      echo "    $error_output"
      exit_code=1
    fi
  fi
done
