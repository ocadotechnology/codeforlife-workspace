#!/bin/bash

RED='\e[31m'
GREEN='\e[32m'
YELLOW='\e[33m'
BLUE='\e[34m'
MAGENTA='\e[35m'
CYAN='\e[36m'
WHITE='\e[37m'
BOLD='\e[1m'
RESET='\e[0m'

function _echo() {
  echo -e "$@${RESET}"
}

function echo_success() {
  _echo "${GREEN}${BOLD}$@"
}

function echo_error() {
  _echo "${RED}${BOLD}$@"

  if [[ -v exit ]]; then exit $exit; fi
}

function echo_warning() {
  _echo "${YELLOW}${BOLD}$@"
}

function echo_info() {
  _echo "${BLUE}${BOLD}$@"
}

function echo_intro() {
  local M=$MAGENTA
  local C=$CYAN
  local Y=$YELLOW

  echo -en "
  ${M}_____          ${Y}_        ______           _      ${M}_  ${C}__
 ${M}/ ____|        ${Y}| |      |  ____|         | |    ${M}(_)${C}/ _|
${M}| |     ${C}___   ${Y}__| | ${M}___  ${Y}| |__ ${M}___  ${C}_ __  ${Y}| |     ${M}_| ${C}|_ ${Y}___
${M}| |    ${C}/ _ \\ ${Y}/ _\` |${M}/ _ \\ ${Y}|  __${M}/ _ \\"
  echo -e "${C}| '__| ${Y}| |    ${M}| |  ${C}_${Y}/ _ \\
${M}| |___${C}| (_) | ${Y}(_| |  ${M}__/ ${Y}| | ${M}| (_) ${C}| |    ${Y}| |____${M}| | ${C}|${Y}|  __/
 ${M}\\_____${C}\\___/ ${Y}\\__,_|${M}\\___| ${Y}|_|  ${M}\\___/${C}|_|    ${Y}|______${M}|_|${C}_| ${Y}\\___|
${RESET}"
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
