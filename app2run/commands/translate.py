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

"""translate module contains the implmentation for the `app2run translate` command.
"""
from typing import Dict, List
import click
from app2run.commands.translation_rules.entrypoint import translate_entrypoint_features
from app2run.config.feature_config_loader import Feature, InputType, FeatureConfig,\
    get_feature_config, get_feature_list_by_input_type
from app2run.commands.translation_rules.scaling import translate_scaling_features
from app2run.commands.translation_rules.concurrent_requests import \
    translate_concurrent_requests_features
from app2run.commands.translation_rules.timeout import translate_timeout_features
from app2run.commands.translation_rules.cpu_memory import translate_app_resources
from app2run.commands.translation_rules.supported_features import translate_supported_features
from app2run.commands.translation_rules.required_flags import translate_add_required_flags
from app2run.common.util import flatten_keys, validate_input

@click.command(short_help="Translate an app.yaml to migrate to Cloud Run.")
@click.option('-a', '--appyaml', help='Path to the app.yaml of the app.')
@click.option('-s', '--service', help='Name of the App Engine service.')
@click.option('-v', '--version', help='App Engine version id.')
@click.option('-p', '--project', help='Name of the project where the App Engine version \
is deployed.')
@click.option('--target-service', help="The name of the service for the Cloud Run app.")
def translate(appyaml, service, version, project, target_service) -> None: # pylint: disable=too-many-arguments
    """Translate command translates an App Engine app.yaml or a deployed version to \
        eqauivalant gcloud command to migrate the GAE App to Cloud Run."""

    input_type, input_data = validate_input(appyaml, service, version, project)
    if not input_type or not input_data:
        return
    target_service = target_service if target_service is not None else \
        _get_service_name(input_data)
    input_flatten_as_appyaml = flatten_keys(input_data, "") if input_type == InputType.APP_YAML \
        else _convert_admin_api_input_to_app_yaml(input_data)
    flags: List[str] = _get_cloud_run_flags(input_data, input_flatten_as_appyaml, \
        input_type, project)
    _generate_output(target_service, flags)

def _convert_admin_api_input_to_app_yaml(admin_api_input_data: Dict):
    input_key_value_pairs = flatten_keys(admin_api_input_data, "")
    feature_config : FeatureConfig = get_feature_config()
    translatable_features = {}
    translatable_features.update(get_feature_list_by_input_type(InputType.ADMIN_API, \
        feature_config.range_limited))
    translatable_features.update(get_feature_list_by_input_type(InputType.ADMIN_API, \
        feature_config.value_limited))
    translatable_features.update(get_feature_list_by_input_type(InputType.ADMIN_API, \
        feature_config.supported))

    merged_keys = [key for key in input_key_value_pairs if key in translatable_features]
    merged_features: List[Feature] = []
    for key in merged_keys:
        merged_features.append(translatable_features[key])
    app_yaml_input = {}
    for feature in merged_features:
        app_yaml_input[feature.path[InputType.APP_YAML.value]] = \
            input_key_value_pairs[feature.path[InputType.ADMIN_API.value]]
    if 'env' in admin_api_input_data and admin_api_input_data['env'] == 'flexible':
        app_yaml_input['env'] = 'flex'
    if 'instanceClass' in admin_api_input_data:
        app_yaml_input['instance_class'] = input_key_value_pairs['instanceClass']
    return app_yaml_input

def _get_cloud_run_flags(input_data: Dict, input_flatten_as_appyaml: Dict, input_type: InputType, \
    project: str):
    feature_config : FeatureConfig = get_feature_config()
    range_limited_features_app_yaml = get_feature_list_by_input_type(InputType.APP_YAML, \
        feature_config.range_limited)
    supported_features = get_feature_list_by_input_type(InputType.APP_YAML, \
        feature_config.supported)
    return translate_concurrent_requests_features(input_flatten_as_appyaml, \
        range_limited_features_app_yaml) + \
           translate_scaling_features(input_flatten_as_appyaml, range_limited_features_app_yaml) + \
           translate_timeout_features(input_flatten_as_appyaml) + \
           translate_app_resources(input_flatten_as_appyaml, range_limited_features_app_yaml) + \
           translate_supported_features(input_flatten_as_appyaml, supported_features, project) + \
           translate_entrypoint_features(input_data, input_type) + \
           translate_add_required_flags()

def _get_service_name(input_data: Dict):
    if 'service' in input_data:
        custom_service_name = input_data['service'].strip()
        if len(custom_service_name) > 0:
            return custom_service_name
    return 'default'

def _generate_output(service_name: str, flags: List[str]):
    """
    example output:
    gcloud run deploy default \
      --cpu=1 \
      --memory=2Gi \
      --timeout=10m
    """
    click.echo("""Warning: not all configuration could be translated,
for more info use app2run list–incompatible-features.""")
    first_line_ending_char = '' if flags is None or len(flags) == 0 else '\\'
    output = f"""
gcloud run deploy {service_name} {first_line_ending_char}
"""
    if flags is not None:
        for i, flag in enumerate(flags):
            # The last flag does not have tailing \
            output += '  '
            output += flag + ' \\' if i < len(flags) - 1 else flag
            output += '\n'
    click.echo(output)
