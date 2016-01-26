apt_require() {
  PACKAGE="${1}"
  dpkg -s "${PACKAGE}" >/dev/null 2>&1 || sudo apt-get install "${PACKAGE}"
}

pyenv_setup() {
  PYTHON="${1}"
  LOCATION="${2}"
  REQUIREMENTS="${3}"

  if [ ! -d "${LOCATION}" ]; then
    virtualenv --python="${PYTHON}" "${LOCATION}" >/dev/null 2>&1
    sed -i '4i VIRTUAL_ENV_DISABLE_PROMPT=1\n' "${LOCATION}/bin/activate"

    if [ -f "${REQUIREMENTS}" ]; then
      . "${LOCATION}/bin/activate"
      pip install --upgrade pip
      pip install -r "${REQUIREMENTS}"
      deactivate
    fi
  fi

  . "${LOCATION}/bin/activate"
}
