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

"""features_helper module contains the functions to access data in the
incompatible_features.yaml file as dataclass types.
"""
from enum import Enum
from dataclasses import dataclass
from os import path as os_path
from typing import Any, Dict, List
import yaml

_CONFIG_PATH = os_path.join(os_path.dirname(__file__), '../config/features.yaml')

class FeatureType(Enum):
    """Enum of feature types."""
    UNSUPPORTED = "unsupported"
    RANGE_LIMITED = "range_limited"

class InputType(Enum):
    """Enum of input types."""
    APP_YAML = "app_yaml"
    ADMIN_API = "admin_api"

@dataclass
class Range:
    """Range represents the range limit of a RangeLimitFeature."""
    min: int
    max: int

@dataclass
class Path:
    """Paths represents the path variants for appyaml and api input data."""
    admin_api: str
    app_yaml: str

@dataclass
class Feature:
    """Feature represents a feature, contains common fields for all features."""
    path: Path

@dataclass
class SupportedFeature(Feature):
    """SupportedFeature represents a supported feature with 1:1 mappings \
        between App Engine and Cloud Run features."""
    flags: List[str]

@dataclass
class UnsupportedFeature(Feature):
    """UnsupportedFeature represents an unsupported Feature."""
    severity: str
    reason: str

@dataclass
class RangeLimitFeature(UnsupportedFeature):
    """RangeLimitFeature represents a range_limited Feature,
    it extends UnsupportedFeature and adds addtional field of range limit."""
    range: Range
    flags: List[str] = None

    def is_within_range(self, val):
        """Check if the given value is within range limit."""
        return self.range['min'] <= val <= self.range['max']

@dataclass
class ValueLimitFeature(UnsupportedFeature):
    """ValueLimitFeature presents a value_limited Feature, it extends
    UnsupportedFeature and adds additional fields to validate compatible value."""
    allowed_values: List[str]
    known_values: List[str]

    def is_value_known(self, val):
        """Check if the given value is known in Cloud Run."""
        return val in self.known_values

    def is_value_allowed(self, val):
        """Check if the given value is allowed in Cloud Run."""
        return val in self.allowed_values

@dataclass()
class FeatureConfig:
    """FeatureConfig represents the incompatible features configuration."""
    unsupported: List[UnsupportedFeature]
    range_limited: List[RangeLimitFeature]
    value_limited: List[ValueLimitFeature]
    supported: List[SupportedFeature]

    def __post_init__(self):
        unsupported_data = [UnsupportedFeature(**f) for f in self.unsupported]
        self.unsupported = unsupported_data
        range_limited_data = [RangeLimitFeature(**f) for f in self.range_limited]
        self.range_limited = range_limited_data
        value_limited_data = [ValueLimitFeature(**f) for f in self.value_limited]
        self.value_limited = value_limited_data
        supported_data = [SupportedFeature(**f) for f in self.supported]
        self.supported = supported_data

def get_feature_config() -> FeatureConfig:
    """Read config data from features yaml and convert data into dataclass types."""
    read_yaml = _read_yaml_file()
    parsed_yaml_dict = _parse_yaml_file(read_yaml)
    return _dict_to_features(parsed_yaml_dict)

def create_unknown_value_feature(feature: UnsupportedFeature, val: str, input_type: InputType) \
    -> UnsupportedFeature:
    """Create an instance of UnsupportedFeature for unknown feature value."""
    reason : str = f'{val} is not a known value for {feature.path[input_type.value]}.'
    return UnsupportedFeature(feature.path, 'unknown',  reason)

def get_feature_list_by_input_type(input_type: InputType, features: List[UnsupportedFeature]) -> \
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
    return {i.path[input_type.value]: i for i in features}

def _read_yaml_file() -> str:
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
