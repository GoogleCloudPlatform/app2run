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
from app2run.config.feature_config_loader import get_feature_list_by_input_type, \
    get_feature_config, FeatureConfig, InputType
from app2run.common.util import ENTRYPOINT_FEATURE_KEYS, flatten_keys, \
    generate_output_flags

_EXCLUDE_FEATURES: List[str] = ENTRYPOINT_FEATURE_KEYS

def translate_supported_features(input_data: Dict, input_type: InputType,\
    project_cli_flag: str) -> List[str]:
    """Translate supported features."""
    feature_config : FeatureConfig = get_feature_config()
    supported_features = get_feature_list_by_input_type(input_type, feature_config.supported)
    input_key_value_pairs = flatten_keys(input_data, "")

    output_flags: List[str] = []
    for key in supported_features:
        if key in input_key_value_pairs:
            # excluded features are handled in separate translation rules.
            if key in _EXCLUDE_FEATURES:
                continue
            feature = supported_features[key]
            input_value = f'"{input_key_value_pairs[key]}"'
            output_flags += generate_output_flags(feature.flags, input_value)

    # env_variables values is a dict, therefore, the feature key 'env_variables' won't be
    # contained in the flatten input_key_value_pairs, it would be contain in the unflatten
    # input_data instead.
    env_variables_key: str = 'env_variables' if input_type == InputType.APP_YAML else 'envVariables'
    if env_variables_key in input_data:
        env_variables_value = _generate_envs_output(input_data[env_variables_key])
        feature = supported_features[env_variables_key]
        output_flags += generate_output_flags(feature.flags, f'"{env_variables_value}"')

    # if service_account is not specified in app.yaml, use the appspot service account:
    # https://cloud.google.com/appengine/docs/standard/go/service-account
    if 'service_account' not in input_key_value_pairs:
        project_id = project_cli_flag if project_cli_flag is not None \
            else _get_project_id_from_gcloud()
        if not project_id:
            click.echo("Warning: unable to determine project id from gcloud config, \
                use the --project flag to provide the project id.")
            return []

        feature = supported_features['service_account']
        default_service_account = f'{project_id}@appspot.gserviceaccount.com'
        output_flags += generate_output_flags(feature.flags, default_service_account)
    return output_flags

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
    for key, value in envs.items():
        output_str += f'{key}={value};'
    # remove the last tailing ;
    return output_str[:-1]
