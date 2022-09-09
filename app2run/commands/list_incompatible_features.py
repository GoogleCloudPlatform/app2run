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

"""list_incompatible_features module contains the implmentation for
the `app2run list-incompatible-features` command.
"""

import os
from typing import Dict, List
import click
import yaml
from app2run.config.feature_config_loader import create_unknown_value_feature, FeatureConfig, \
    get_feature_config, InputType, UnsupportedFeature, get_feature_list_by_input_type
from app2run.common.util import flatten_keys

@click.command(short_help="List incompatible App Engine features to migrate to Cloud Run.")
@click.option('-a', '--appyaml', help='Path to the app.yaml of the app.')
@click.option('-s', '--service', help='Name of the App Engine service.')
@click.option('-v', '--version', help='App Engine version id.')
@click.option('-p', '--project', help='Name of the project where the App Engine version \
is deployed.')
def list_incompatible_features(appyaml, service, version, project) -> None:
    """list_incompatible_features command validates the input app.yaml or deployed app version
    to identify any incompatible features to migrate the App Engine app to Cloud Run."""
    if not _validate_input(appyaml, service, version):
        return
    input_type = InputType.APP_YAML if (service is None and version is None) \
        else InputType.ADMIN_API
    if input_type is InputType.APP_YAML and appyaml is None:
        # default input --appyaml to be `app.yaml` if input type is APP_YAML
        # and no --appyaml is provided.
        appyaml = 'app.yaml'
    input_data = _get_input_data_by_input_type(input_type, appyaml, service, version, project)
    if input_data is None:
        click.echo('[Error] Failed to read input data.')
        return
    incompatible_list = _check_for_incompatibility(input_data, input_type)
    _generate_output(incompatible_list, input_type)

def _get_input_data_by_input_type(input_type: InputType, appyaml, service=None, \
    version=None, project=None) -> Dict:
    # deployed version is input type
    if input_type == InputType.ADMIN_API:
        gcloud_command = f'gcloud app versions describe {version} --service={service}'
        if project is not None:
            gcloud_command += f'--project={project}'
        gcloud_output = os.popen(gcloud_command)
        return yaml.safe_load(gcloud_output)

    # appyaml is input type
    try:
        with open(appyaml, 'r', encoding='utf8') as file:
            appyaml_data = yaml.safe_load(file.read())
            if appyaml_data is None:
                click.echo(f'{file.name} is empty.')
            return appyaml_data
    except IOError:
        click.echo('app.yaml does not exist.')
    return None

def _validate_input(appyaml, service, version):
    use_app_yaml = appyaml is not None
    use_deployed_version = service is not None and version is not None
    if use_app_yaml and use_deployed_version:
        click.echo("[Error] Invalid input, only one of app.yaml or deployed version could be \
used as input. Use --appyaml flag to specify the app.yaml, use --service and --version \
to specify the deployed version.")
        return False
    return True

def _check_for_incompatibility(input_data: Dict, input_type: InputType) -> List[UnsupportedFeature]:
    """Check for incompatibility features in the input yaml, it flatterns the nested input into a
    one-level key-value pairs and compare it with the configured list of incompatible features."""
    incompatible_list : List[UnsupportedFeature] = []

    feature_config : FeatureConfig = get_feature_config()
    unsupported_features = get_feature_list_by_input_type(input_type, feature_config.unsupported)
    range_limited_features =  get_feature_list_by_input_type(input_type, \
        feature_config.range_limited)
    value_restricted_features = get_feature_list_by_input_type(input_type, \
        feature_config.value_limited)

    input_key_value_pairs = flatten_keys(input_data, "")

    for key, val in input_key_value_pairs.items():
        # Check for unsupported features.
        if key in unsupported_features:
            incompatible_list.append(unsupported_features[key])
        # Check for range_limited features.
        elif key in range_limited_features:
            feature = range_limited_features[key]
            if not feature.is_within_range(val):
                incompatible_list.append(range_limited_features[key])
        # Check for value_restricted features.
        elif key in value_restricted_features:
            feature = value_restricted_features[key]
            if not feature.is_value_known(val):
                incompatible_list.append(create_unknown_value_feature(feature, val, input_type))
            elif not feature.is_value_allowed(val):
                incompatible_list.append(value_restricted_features[key])

    return incompatible_list

def _generate_output(incompatible_features: List[UnsupportedFeature], input_type: InputType) \
    -> None:
    """Generate readable output for features compability check result."""
    if len(incompatible_features) == 0:
        click.echo("No incompatibilities found.")
        return

    click.echo("summary:")
    click.echo(f'  major: {len(incompatible_features)}')
    click.echo("incompatible_features:")
    click.echo(yaml.dump(_get_display_features(incompatible_features, input_type)))

def _get_display_features(features: List[UnsupportedFeature], input_type: InputType) -> List:
    """Convert a List[Tuple] to List[Object] in order to print desired output format."""
    _features_display = []
    for feature in features:
        _features_display.append(
            {
                "path": feature.path[input_type.value],
                "severity": feature.severity,
                "reason": feature.reason
            }
        )
    return _features_display
