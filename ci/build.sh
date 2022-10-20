#!/bin/bash

# Fail on any error.
set -e

# Display commands being run.
# WARNING: please only enable 'set -x' if necessary for debugging, and be very
#  careful if you handle credentials (e.g. from Keystore) with 'set -x':
#  statements like "export VAR=$(cat /tmp/keystore/credentials)" will result in
#  the credentials being printed in build logs.
#  Additionally, recursive invocation with credentials as command-line
#  parameters, will print the full command, with credentials, in the build logs.
set -x

PYTHON_VERSION="3.9.5"

function setup_python_virtual_env {
  echo "Python versions available."
  pyenv versions
  pyenv global $1
  python -m venv ./kokoro_env
  source ./kokoro_env/bin/activate
  echo "Python version details in virtual env."
  python --version
  pip --version
  echo "Installing pylint"
  python3 -m pip install pylint
  echo "Installing pytest"
  python3 -m pip install pytest
}

function install_app2run_cli {
  echo "installing app2run"
  python3 -m pip install --editable .
  which app2run
  app2run --help
}

function run_pylint {
  find ./app2run -type f -name "*.py" | xargs pylint
}

function run_unit_test {
  py.test
}

setup_python_virtual_env $PYTHON_VERSION
install_app2run_cli
run_pylint
run_unit_test