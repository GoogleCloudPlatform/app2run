# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Translation rule for entrypoint."""

from os import path
from typing import Dict, List
import click
from app2run.common.util import ENTRYPOINT_FEATURE_KEYS, RUNTIMES_WITH_PROCFILE_ENTRYPOINT, \
    flatten_keys, generate_output_flags
from app2run.config.feature_config_loader import InputType

_DEFAULT_PYTHON_ENTRYPOINT = 'gunicorn -b :$PORT main:app'
# Cloud Run service must listen on 0.0.0.0 host,
# ref https://cloud.google.com/run/docs/container-contract#port
_DEFAULT_RUBY_ENTRYPOINT = 'bundle exec ruby app.rb -o 0.0.0.0'
_DEFAULT_ENTRYPOINT_INFO_FORMAT = '[Info] Default entrypoint point for {runtime} is : \
"{entrypoint}", retry `app2run translate` with the --command="{entrypoint}" flag.'

def translate_entrypoint_features(input_data: Dict, input_type: InputType, \
    supported_features_app_yaml: Dict, command: str=None) -> List[str]:
    """Tranlsate entrypoint from App Engine app to entrypoint for equivalent Cloud Run app."""
    input_key_value_pairs = flatten_keys(input_data, "")
    if input_type is InputType.ADMIN_API:
        return _generate_entrypoint_admin_api(input_key_value_pairs, command)
    return _generate_entrypoint_app_yaml(input_key_value_pairs, supported_features_app_yaml)

def _generate_entrypoint_admin_api(input_key_value_pairs: Dict, command: str=None):
    # entrypoint is not included in the `gcloud app versions describe` output for GAE apps \
    # deployed from source, it needs to be provided via the --command flag when calling the \
    # app2run translate CLI.
    if command is None:
        click.echo('Warning: entrypoint for the app is not detected/provided, if an entrypoint is \
needed to start the app, please use the `--command` flag to specify the entrypoint for the App.')
        _print_default_entryoint_per_runtime(input_key_value_pairs)
        return []
    if 'runtime' in input_key_value_pairs:
        runtime = input_key_value_pairs['runtime']
        if runtime in RUNTIMES_WITH_PROCFILE_ENTRYPOINT:
            click.echo(f'generating a procfile with runtime {runtime}, entrypoint {command}')
            _generate_procfile(runtime, command)
            return []
    return generate_output_flags(['--command'], f'"{command}"')

def _generate_entrypoint_app_yaml(input_key_value_pairs: Dict, supported_features_app_yaml: Dict):
    if _should_generate_procfile(input_key_value_pairs):
        runtime = input_key_value_pairs['runtime']
        entrypoint = _get_entrypoint_from_input(input_key_value_pairs)
        # entrypoint is not specified at input, use the default entrypoint
        if not entrypoint:
            entrypoint = _get_default_entrypoint_by_runtime(input_key_value_pairs)
        _generate_procfile(runtime, entrypoint)
        return []
    feature_key = 'entrypoint'
    if feature_key in input_key_value_pairs:
        feature = supported_features_app_yaml[feature_key]
        input_value = f'"{input_key_value_pairs[feature_key]}"'
        return generate_output_flags(feature.flags, input_value)
    return []

def _should_generate_procfile(input_key_value_pairs: Dict) -> bool:
    if 'runtime' not in input_key_value_pairs:
        return False
    runtime = input_key_value_pairs['runtime']
    if runtime not in RUNTIMES_WITH_PROCFILE_ENTRYPOINT:
        return False
    return True

def _generate_procfile(runtime: str, entrypoint: str):
    if not _procfile_exists():
        with open('Procfile', 'w', encoding='utf8') as file:
            file.write(f'web: {entrypoint}')
            click.echo(f'[Info] A Procfile is created with entrypoint "{entrypoint}", \
this is needed to deploy Apps from source with {runtime} runtime to Cloud Run using Buildpacks.')
        return

    if not _procfile_contains_entrypoint(entrypoint):
        click.echo(f'[Warning] Entrypoint "{entrypoint}" is not found at existing Procfile, \
please add "web: {entrypoint}" to the existing Procfile.')

def _procfile_exists() -> bool:
    return path.exists('Procfile')

def _procfile_contains_entrypoint(entrypoint: str) -> bool:
    if not _procfile_exists():
        return False
    with open('Procfile', 'r', encoding='utf8') as file:
        procfile_content = file.read()
        if entrypoint in procfile_content:
            return True
    return False

def _get_entrypoint_from_input(input_key_value_pairs: Dict) -> str:
    for key in ENTRYPOINT_FEATURE_KEYS:
        if key in input_key_value_pairs:
            return input_key_value_pairs[key]
    return ''

def _get_default_entrypoint_by_runtime(input_key_value_pairs) -> str:
    if 'runtime' in input_key_value_pairs:
        runtime = input_key_value_pairs['runtime']
        if runtime.startswith('python'):
            # Check if requirements.txt exists and contains gunicorn as a dependency
            _generate_requirement_file()
            return _DEFAULT_PYTHON_ENTRYPOINT
        if runtime.startswith('ruby'):
            return _DEFAULT_RUBY_ENTRYPOINT
    return ''

def _generate_requirement_file():
    _file_exist = path.exists('requirements.txt')
    if _file_exist:
        with open('requirements.txt', 'r', encoding='utf8') as file:
            _file_content = file.read()
        if "gunicorn" not in _file_content:
            click.echo('[Warning] gunicorn is not found at requirements.txt, \
please add "gunicorn" to the existing requirements.txt in order to deploy Apps \
from source to Cloud Run using Buildpacks.')
    else:
        with open('requirements.txt', 'w', encoding='utf8') as file:
            file.write('gunicorn')
            click.echo('[Info] A requirements.txt is created with gunicorn as a dependency, \
this is needed to deploy Apps from source with python runtime to Cloud Run using Buildpacks.')

def _print_default_entryoint_per_runtime(input_key_value_pairs):
    if 'runtime' in input_key_value_pairs:
        runtime = input_key_value_pairs['runtime']
        if runtime.startswith('python'):
            click.echo(_DEFAULT_ENTRYPOINT_INFO_FORMAT.format(runtime=runtime, \
                entrypoint=_DEFAULT_PYTHON_ENTRYPOINT))
            click.echo(f'[Info] Add "gunicorn" as a dependency to requirements.txt because it \
is used for the {runtime}\'s default entrypoint "{_DEFAULT_PYTHON_ENTRYPOINT}"')
        if runtime.startswith('ruby'):
            click.echo(_DEFAULT_ENTRYPOINT_INFO_FORMAT.format(runtime=runtime, \
                entrypoint=_DEFAULT_RUBY_ENTRYPOINT))
