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
from app2run.config.feature_config_loader import get_feature_list_by_input_type, InputType, \
    get_feature_config, FeatureConfig

def translate_entrypoint_features(input_data: Dict, input_type: InputType) -> List[str]:
    """Tranlsate entrypoint from App Engine app to entrypoint for equivalent app at Cloud Run."""
    input_key_value_pairs = flatten_keys(input_data, "")
    feature_key = _get_feature_key(input_type)
    if feature_key not in input_key_value_pairs:
        return []
    feature_config : FeatureConfig = get_feature_config()
    supported_features = get_feature_list_by_input_type(input_type, feature_config.supported)
    if _should_generate_procfile(input_key_value_pairs):
        _generate_procfile(input_key_value_pairs)
        return []

    feature = supported_features[feature_key]
    input_value = input_value = f'"{input_key_value_pairs[feature_key]}"'
    return generate_output_flags(feature.flags, input_value)

def _should_generate_procfile(input_key_value_pairs: Dict) -> bool:
    if 'runtime' not in input_key_value_pairs:
        return False
    runtime = input_key_value_pairs['runtime']
    entrypoint = _get_entrypoint_from_input(input_key_value_pairs)
    if runtime not in RUNTIMES_WITH_PROCFILE_ENTRYPOINT:
        return False
    if entrypoint == '':
        return False
    return True

def _generate_procfile(input_key_value_pairs: Dict):
    runtime = input_key_value_pairs['runtime']
    entrypoint = _get_entrypoint_from_input(input_key_value_pairs)
    if not _procfile_exists():
        with open('Procfile', 'w', encoding='utf8') as file:
            file.write(f'web: {entrypoint}')
            click.echo(f'[Info] A Procfile is created with entrypoint "{entrypoint}", \
this is needed to deploy Apps from source with {runtime} runtime to Cloud Run using Buildpacks.')
        return

    if not _procfile_contains_entrypoint(entrypoint):
        click.echo(f'[Warning] Entrypoint "{entrypoint}" is not found at existing Procfile, \
please add "web: {entrypoint}" to the existing Procfile.')

def _get_feature_key(input_type: InputType) -> str:
    if input_type is InputType.APP_YAML:
        return 'entrypoint'
    return 'entrypoint.shell'

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
