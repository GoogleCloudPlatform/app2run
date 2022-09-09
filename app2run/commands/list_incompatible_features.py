
"""list_incompatible_features module contains the implmentation for
the `app2run list-incompatible-features` command.
"""

from typing import Dict, List
import click
import yaml
from app2run.config.feature_config_loader import create_unknown_value_feature, FeatureConfig, \
    get_feature_config, InputType, UnsupportedFeature, get_feature_list_by_input_type
from app2run.common.util import flatten_keys, validate_input

@click.command(short_help="List incompatible App Engine features to migrate to Cloud Run.")
@click.option('-a', '--appyaml', help='Path to the app.yaml of the app.')
@click.option('-s', '--service', help='Name of the App Engine service.')
@click.option('-v', '--version', help='App Engine version id.')
@click.option('-p', '--project', help='Name of the project where the App Engine version \
is deployed.')
def list_incompatible_features(appyaml, service, version, project) -> None:
    """list_incompatible_features command validates the input app.yaml or deployed app version
    to identify any incompatible features to migrate the App Engine app to Cloud Run."""
    input_type, input_data = validate_input(appyaml, service, version, project)
    if not input_type or not input_data:
        return
    incompatible_list = _check_for_incompatibility(input_data, input_type)
    _generate_output(incompatible_list, input_type)

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
