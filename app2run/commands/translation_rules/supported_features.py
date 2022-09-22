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

"""Translate supported features found at app.yaml to equivalent Cloud Run flags."""

import os
import re
from typing import Dict, List
import click
from app2run.common.util import ENTRYPOINT_FEATURE_KEYS, generate_output_flags, \
    get_feature_key_from_input

_ALLOW_ENV_VARIABLES_KEY: str = 'env_variables'
_ALLOW_SERVICE_ACCOUNT_KEY: str = 'service_account'
_EXCLUDE_FEATURES: List[str] = ENTRYPOINT_FEATURE_KEYS
_EXCLUDE_FEATURES.append(_ALLOW_ENV_VARIABLES_KEY)

def translate_supported_features(input_data: Dict, supported_features: Dict, \
    project_cli_flag: str) -> List[str]:
    """Translate supported features."""
    output_flags: List[str] = []
    for key in supported_features:
        if key in input_data:
            # excluded features are handled in separate translation rules.
            if key in _EXCLUDE_FEATURES:
                continue
            feature = supported_features[key]
            input_value = f'"{input_data[key]}"'
            output_flags += generate_output_flags(feature.flags, input_value)

    output_flags += _get_output_flags_for_env_variables(input_data, \
        supported_features)
    output_flags += _get_output_flags_for_default_service_account(input_data, \
        supported_features, project_cli_flag)
    return output_flags

def _get_output_flags_for_env_variables(input_data: Dict, supported_features: Dict):
    # env_variables values is a dict, therefore, the feature key 'env_variables' won't be
    # contained in the flatten input_key_value_pairs, it would be contain in the unflatten
    # input_data instead.
    output_flags: List[str] = []
    env_variables_key_from_input = get_feature_key_from_input(input_data, \
        [_ALLOW_ENV_VARIABLES_KEY])
    if env_variables_key_from_input:
        env_variables_value = _generate_envs_output(input_data[env_variables_key_from_input])
        feature = supported_features[env_variables_key_from_input]
        output_flags += generate_output_flags(feature.flags, f'"{env_variables_value}"')
    return output_flags

def _get_output_flags_for_default_service_account(input_data: Dict, \
    supported_features: Dict, project_cli_flag: str):
    input_has_service_account_key = get_feature_key_from_input(input_data, \
        [_ALLOW_SERVICE_ACCOUNT_KEY])
    # if service_account is not specified in app.yaml/deployed version, use the default \
    # service account: https://cloud.google.com/appengine/docs/standard/go/service-account
    if not input_has_service_account_key:
        # if input doesn't contain service account, try to generate the default \
        # service account with the project id:
        # - check if a project id is provided via the --project cli flag.
        # or
        # - check if gcloud config has project id .
        project_id = project_cli_flag if project_cli_flag is not None \
            else _get_project_id_from_gcloud()
        if not project_id:
            click.echo("Warning: unable to determine project id from gcloud config, \
                use the --project flag to specify the project id of the deployed \
                    App Engine version.")
            return []

        feature = supported_features['service_account']
        default_service_account = f'"{project_id}@appspot.gserviceaccount.com"'
        return generate_output_flags(feature.flags, default_service_account)
    return []

def _get_project_id_from_gcloud():
    output = os.popen('gcloud config list').read()
    project_id = re.search(r'(?<=project = )([\w-]+)', output)
    if project_id is not None:
        return project_id.group()
    return ""

def _generate_envs_output(envs: Dict) -> str:
    if len(envs.items()) == 0:
        return ''
    output_str = ''
    # if value contains comma, use a different delimiter
    # see https://cloud.google.com/run/docs/configuring/environment-variables#escaping
    value_contains_comma = False
    for key, value in envs.items():
        if ',' in value:
            value_contains_comma = True
            break
    delimiter = '@' if value_contains_comma else ','
    output_str = '' if delimiter == ',' else f'^{delimiter}^'
    for key, value in envs.items():
        output_str += f'{key}={value}{delimiter}'
    # remove the last tailing delimiter
    return output_str[:-1]
