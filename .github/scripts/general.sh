#!/bin/bash

RED='\e[31m'
GREEN='\e[32m'
YELLOW='\e[33m'
BLUE='\e[34m'
MAGENTA='\e[35m'
CYAN='\e[36m'
WHITE='\e[37m'
BOLD='\e[1m'
UNDERLINE='\e[4m'
OVERLINE='\e[53m'
RESET='\e[0m'

function _echo() {
  echo -e $options "$@${RESET}"
}

function echo_bold() {
  _echo "${BOLD}$@"
}

function echo_success() {
  echo_bold "${GREEN}$@"
}

function echo_error() {
  echo_bold "${RED}$@"

  if [[ -v exit ]]; then exit $exit; fi
}

function echo_warning() {
  echo_bold "${YELLOW}$@"
}

function echo_info() {
  echo_bold "${BLUE}$@"
}

function echo_divider() {
  printf "${BOLD}%*s${RESET}\n" "${COLUMNS:-80}" '' | tr ' ' '-'
}

function echo_h1() {
  echo_divider
  echo_bold "$@"
  echo_divider
}

function echo_h2() {
  echo_bold "${UNDERLINE}${OVERLINE}$@"
}

function eval_bool() {
  local bool="$1"

  bool=$(echo "$bool" | tr '[:upper:]' '[:lower:]')

  if [ "$bool" = "1" ] || [ "$bool" = "true" ] || [ "$bool" = "t" ]; then
    return 0
  elif [ "$bool" = "0" ] || [ "$bool" = "false" ] || [ "$bool" = "f" ]; then
    return 1
  fi

  exit=1 echo_error "Attempted to evaluate invalid boolean value: \"$bool\"."
}

function trim_spaces() {
  echo "$@" | sed --regexp-extended 's/^[[:space:]]*|[[:space:]]*$//g'
}
