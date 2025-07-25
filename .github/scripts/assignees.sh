#!/bin/bash

function _format_assignee_ids() {
  echo "$@" | sed 's/ /","/g; s/^/"/; s/$/"/'
}

function add_assignee() {
  local assignable_id="$1"
  local assignee_ids="${@:2}"

  assignee_ids="$(_format_assignee_ids "$assignee_ids")"

  gh api graphql -f query='
    mutation {
      addAssignee: addAssigneesToAssignable(input: {
        assignableId: "'$assignable_id'"
        assigneeIds: ['$assignee_ids']
      }) {
        assignable { ... on Issue { id } }
      }
    }'
}

function remove_assignee() {
  local assignable_id="$1"
  local assignee_ids="${@:2}"

  assignee_ids="$(_format_assignee_ids "$assignee_ids")"

  gh api graphql -f query='
    mutation {
      removeAssignee: removeAssigneesFromAssignable(input: {
        assignableId: "'$assignable_id'"
        assigneeIds: ['$assignee_ids']
      }) {
        assignable { ... on Issue { id } }
      }
    }'
}
