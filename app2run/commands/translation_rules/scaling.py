"""Translation rule for scaling features."""

from enum import Enum
from typing import Dict, List
import click
from app2run.config.feature_config_loader import FeatureConfig, InputType, \
    RangeLimitFeature, get_feature_list_by_input_type
from app2run.common.util import generate_output_flags, get_features_by_prefix, \
    flatten_keys

class ScalingTypeAppYaml(Enum):
    """Enum of scaling types."""
    AUTOMATIC_SCALING = "automatic_scaling"
    MANUAL_SCALING = 'manual_scaling'
    BASIC_SCALING = 'basic_scaling'

_SCALING_FEATURE_KEYS_ALLOWED_LIST: Dict = {
    ScalingTypeAppYaml.AUTOMATIC_SCALING: ['min_num_instances', 'max_num_instances', \
        'min_instances', 'max_instances'],
    ScalingTypeAppYaml.MANUAL_SCALING: ['instances'],
    ScalingTypeAppYaml.BASIC_SCALING: ['max_instances']
}

def translate_scaling_features(input_data: Dict, input_type: InputType, feature_config: \
    FeatureConfig) -> List[str]:
    """Translate scaling features. Translation rule:
        - Only one of the scaling options could be specified:
            - automatic_scaling
            - manual_scaling
            - basic_scaling.
    """
    scaling_types_used = _get_scaling_features_used(input_data)
    range_limited_features = get_feature_list_by_input_type(input_type, \
        feature_config.range_limited)
    if len(scaling_types_used) == 0:
        return []
    if len(scaling_types_used) > 1:
        click.echo('Warning: More than one scaling type is defined, \
            only one scaling option should be used.')
        return []

    scaling_type: ScalingTypeAppYaml = scaling_types_used[0]
    return _get_output_flags(input_data, range_limited_features, scaling_type)

def _get_output_flags(input_data: Dict, range_limited_features: List[RangeLimitFeature], \
    scaling_type: ScalingTypeAppYaml) -> List[str]:
    input_key_value_pairs = flatten_keys(input_data, "")
    # Get feature keys from the input app.yaml that has the scaling type
    # (e.g. 'automatic_scaling') prefix.
    input_feature_keys = get_features_by_prefix(input_key_value_pairs, \
        scaling_type.value)
    # Filter the input_feature_keys by allowed_list, this is to avoid processing other
    # scaling features such as `automatic_scaling.max_concurrent_requests` and
    # `automatic_scaling.target_concurrent_requests`, etc.
    allowed_keys = _SCALING_FEATURE_KEYS_ALLOWED_LIST[scaling_type]
    allowed_input_feature_keys = [key for key in input_feature_keys \
        if key.split('.')[1] in allowed_keys]
    output_flags: List[str] = []
    for key in allowed_input_feature_keys:
        input_value = input_key_value_pairs[key]
        range_limited_feature = range_limited_features[key]
        output_flags += _get_output_flags_by_scaling_type(key, \
            range_limited_feature, input_value)
    return output_flags

def _get_output_flags_by_scaling_type(feature_key: str, \
    range_limited_feature: RangeLimitFeature, input_value: int) -> List[str]:
    if input_value < range_limited_feature.range['min']:
        click.echo(f"Warning: {feature_key} has a negagive value of {input_value}, \
            minimum value is {range_limited_feature.range['min']}.")
        return []

    target_value = range_limited_feature.range['max']
    if range_limited_feature.is_within_range(input_value):
        target_value = input_value
    return generate_output_flags(range_limited_feature.flags, target_value)

def _get_scaling_features_used(input_data: Dict) -> List[ScalingTypeAppYaml]:
    scaling_features: List[ScalingTypeAppYaml] = []
    if ScalingTypeAppYaml.AUTOMATIC_SCALING.value in input_data:
        scaling_features.append(ScalingTypeAppYaml.AUTOMATIC_SCALING)
    if ScalingTypeAppYaml.MANUAL_SCALING.value in input_data:
        scaling_features.append(ScalingTypeAppYaml.MANUAL_SCALING)
    if ScalingTypeAppYaml.BASIC_SCALING.value in input_data:
        scaling_features.append(ScalingTypeAppYaml.BASIC_SCALING)
    return scaling_features
