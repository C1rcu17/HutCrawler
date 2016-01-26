#!/bin/sh -e

HOME="$(dirname "$(readlink -e "${0}")")"
. "${HOME}/common.sh"

apt_require libxml2-dev
apt_require libxslt1-dev
apt_require zlib1g-dev

pyenv_setup "python3" "${HOME}/py3env" "${HOME}/requirements.txt"

exec python "${HOME}/app.py" "${@}"
