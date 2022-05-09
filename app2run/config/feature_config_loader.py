
"""features_helper module contains the functions to access data in the
incompatible_features.yaml file as dataclass types.
"""
from enum import Enum
from dataclasses import dataclass
from os import path as os_path
from typing import Any, Dict, List
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
    """Paths represents the path variants for appyaml and api input data."""
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
    """RangeLimitFeature represents a range_limited Feature,
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
        unsupported_data = [UnsupportedFeature(**f) for f in self.unsupported]
        self.unsupported = unsupported_data
        range_limited_data = [RangeLimitFeature(**f) for f in self.range_limited]
        self.range_limited = range_limited_data

def get_feature_config() -> FeatureConfig:
    """Read config data from features yaml and convert data into dataclass types."""
    read_yaml = _read_yaml_file()
    parsed_yaml_dict = _parse_yaml_file(read_yaml)
    return _dict_to_features(parsed_yaml_dict)

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
