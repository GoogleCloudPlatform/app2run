
"""list_incompatible_features module contains the implmentation for
the `app2run list-incompatible-features` command.
"""

from dataclasses import dataclass
from enum import Enum
from os import path as os_path
from typing import Any, Dict, List
import click
import yaml

_CONFIG_PATH = os_path.join(os_path.dirname(__file__), '../config/incompatible_features.yaml')

class FeatureType(Enum):
    """Enum of feature types."""
    UNSUPPORTED = "unsupported"
    RANGE_LIMITED = "range_limited"

class InputType(Enum):
    """Enum of input types."""
    APP_YAML = "app_yaml"

@dataclass
class Range:
    """Range represents the range limit of a RangeLimitFeature."""
    min: int
    max: int

@dataclass
class Path:
    """Paths reprents the path variants for appyaml and api input data."""
    admin_api: str
    app_yaml: str

@dataclass
class UnsupportedFeature:
    """Feature represents an unsupported Feature."""
    path: Path
    severity: str
    reason: str

@dataclass
class RangeLimitFeature(UnsupportedFeature):
    """RangeLimitFeature presents a range_limited Feature,
    it extends UnsupportedFeature and adds addtional field of range limit."""
    range: Range

    def is_within_range(self, val):
        """Check if the given value is within range limit."""
        return self.range['min'] <= val <= self.range['max']

@dataclass()
class FeatureConfig:
    """FeatureConfig represents the incompatible features configuration."""
    unsupported: List[UnsupportedFeature]
    range_limited: List[RangeLimitFeature]

    def __post_init__(self):
        unsupported_data = []
        for feature in self.unsupported:
            unsupported_data.append(UnsupportedFeature(**feature))
        self.unsupported = unsupported_data
        range_limited_data = []
        for feature in self.range_limited:
            range_limited_data.append(RangeLimitFeature(**feature))
        self.range_limited = range_limited_data

@click.command(short_help="List incompatible App Engine features to migrate to Cloud Run.")
@click.option('-a', '--appyaml', default='app.yaml', show_default=True,
              help='Path to the app.yaml of the app.', type=click.File())
def list_incompatible_features(appyaml) -> None:
    """list_incompatible_features command validates the input app.yaml or deployed app version
    to identify any incompatible features to migrate the App to Cloud Run."""

    input_data = yaml.safe_load(appyaml.read())
    if input_data is None:
        click.echo(f'{appyaml.name} is empty.')
        return

    incompatible_list = _check_for_incompatibility(input_data, InputType.APP_YAML)
    _generate_output(incompatible_list, InputType.APP_YAML)

def _check_for_incompatibility(input_data: Dict, input_type: InputType) -> List[UnsupportedFeature]:
    """Check for incompatibility features in the input yaml, it flatterns the nested input into a
    one-level key-value pairs and compare it with the configured list of incompatible features."""
    incompatible_list : List[UnsupportedFeature] = []

    read_yaml = _read_yaml_file()
    parsed_yaml_dict = _parse_yaml_file(read_yaml)
    feature_config = _dict_to_features(parsed_yaml_dict)

    unsupported_features = _get_feature_list_by_input_type(input_type, feature_config.unsupported)
    range_limited_features =  _get_feature_list_by_input_type(input_type, \
        feature_config.range_limited)

    input_key_value_pairs = _flatten_keys(input_data, "")

    for key, val in input_key_value_pairs.items():
        # Check for unsupported features.
        if key in unsupported_features:
            incompatible_list.append(unsupported_features[key])
        # Check for range_limited features.
        elif key in range_limited_features:
            feature = range_limited_features[key]
            if not feature.is_within_range(val):
                incompatible_list.append(range_limited_features[key])

    return incompatible_list

def _get_feature_list_by_input_type(input_type: InputType, features: List[UnsupportedFeature]) -> \
    Dict[str, UnsupportedFeature]:
    """Construct a dictionary with the path as the key, the Feature as the value based on
    input type. e.g:

    input:
        input_type: appyaml,
        features: [
            {
                path: {
                    app_yaml: 'inbound_services',
                    admin_api: 'inboundServices'
                },
                severity: 'major',
                reason: 'CR does not support GAE bundled services.'
            }
        ]

    output:
        {
            'inbound_services': {
                path: {
                    app_yaml: 'inbound_services',
                    admin_api: 'inboundServices'
                },
                severity: 'major',
                reason: 'CR does not support GAE bundled services.'
            }
        }
    """
    feature_dict : Dict[str, UnsupportedFeature] = {}
    for i in features:
        path = i.path[input_type.value]
        feature_dict[path] = i
    return feature_dict

def _read_yaml_file():
    """Read the config yaml file of incompabilbe features."""
    with open(_CONFIG_PATH, \
        'r', encoding='utf8') as incompatible_features_yaml_file:
        return incompatible_features_yaml_file.read()

def _parse_yaml_file(yaml_string: str) -> Dict[Any, Any]:
    """Parse the input string as yaml file."""
    return yaml.safe_load(yaml_string)

def _dict_to_features(parsed_yaml: Dict[Any, Any]) -> FeatureConfig:
    """Convert the input dictionary into FeatureConfig type."""
    return FeatureConfig(**parsed_yaml)

def _flatten_keys(input_data: Dict, parent_path: str) -> Dict[str, Any]:
    """Flattern nested paths (root to leaf) of a dictionary. For example:
    Input: {
        "resources": {
            "cpu": 5,
            "memory_gb": 10
        }
    }

    output: {
        "resources.cpu": 5,
        "resources.memory_gb": 10
    }
    """
    paths: Dict[str, str] = {}
    for key in input_data:
        curr_path = f'{parent_path}.{key}' if parent_path else key
        if not isinstance(input_data[key], dict):
            paths[curr_path] = input_data[key]
        else:
            paths.update(_flatten_keys(input_data[key], curr_path))
    return paths

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
