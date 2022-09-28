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
import tempfile
from os import path as os_path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader
import click
from click_option_group import optgroup
import yaml
from app2run.config.feature_config_loader import FeatureConfig, \
    get_feature_config, InputType, UnsupportedFeature, get_feature_list_by_input_type
from app2run.common.util import flatten_keys, validate_input, get_project_id_from_gcloud

_TEMPLATE_PATH = os_path.join(os_path.dirname(__file__), '../config/')

@click.command(short_help="List incompatible App Engine features to migrate to Cloud Run.")
@optgroup.group('APP.YAML', help='The option(s) for using an app.yaml as an input.')
@optgroup.option('-a', '--appyaml', help='Path to the app.yaml of the app.')
@optgroup.group('ADMIN API', help='The option(s) for using a deployed version as an input.')
@optgroup.option('-s', '--service', help='Service name of a deployed App Engine version.')
@optgroup.option('-v', '--version', help='Version id of a deployed App Engine version.')
@optgroup.option('-p', '--project', help='Name of the project where the App Engine version \
is deployed.')
@optgroup.group('OTHERS')
@optgroup.option('-o', '--output', default='yaml', show_default=True, type=click.Choice(['yaml', \
    'html']), help='Output format of the list-incompatible-features command.')
def list_incompatible_features(appyaml, service, version, project, output) -> None:
    """list_incompatible_features command validates the input app.yaml or deployed app version
    to identify any incompatible features to migrate the App Engine app to Cloud Run."""
    input_type, input_data = validate_input(appyaml, service, version, project)
    if not input_type or not input_data:
        return
    incompatible_list = _check_for_incompatibility(input_data, input_type)
    appyaml = 'app.yaml' if appyaml is None else appyaml
    input_name = _generate_input_name(input_type, appyaml, service, version, project)
    _generate_output(incompatible_list, input_type, output, input_name)

def _generate_input_name(input_type, appyaml, service, version, project_cli_flag) -> str:
    if input_type == InputType.APP_YAML :
        return appyaml
    project_id = project_cli_flag if project_cli_flag is not None \
        else get_project_id_from_gcloud()
    return f'{project_id}/{service}/{version}'

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
            if not feature.validate(val):
                incompatible_list.append(range_limited_features[key])
        # Check for value_restricted features.
        elif key in value_restricted_features:
            feature = value_restricted_features[key]
            if not feature.validate(val):
                incompatible_list.append(feature)

    return incompatible_list

def _generate_output(incompatible_features: List[UnsupportedFeature], input_type: InputType, \
    output: str,  input_name: str) -> None:
    """Generate readable output for features compability check result."""
    click.echo(f"list-incompatible-features output for {input_name}:\n")
    if len(incompatible_features) == 0:
        click.echo("No incompatibilities found.")
        return
    if output is not None and output == 'html'.casefold():
        _genertate_html_output(incompatible_features, input_type)
        return

    click.echo("Summary:")
    click.echo(f'  major: {len(incompatible_features)}')
    click.echo("incompatible_features:")
    click.echo(yaml.dump(_get_display_features(incompatible_features, input_type)))

def _genertate_html_output(incompatible_features: List[UnsupportedFeature], input_type: InputType):
    environment = Environment(loader=FileSystemLoader(_TEMPLATE_PATH))
    incompatible_features.sort(key=lambda x: (x.severity, x.path[input_type.value]))
    temp_dir = tempfile.mkdtemp()
    results_filename = f'{temp_dir}/incompatible_features.html'
    results_template = environment.get_template("output_tmpl.html")
    context = {
        "incompatible_features": incompatible_features,
        "input_type": input_type
    }
    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        click.secho(f'Html output of incompatible features: {results_filename}', fg='green')

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
