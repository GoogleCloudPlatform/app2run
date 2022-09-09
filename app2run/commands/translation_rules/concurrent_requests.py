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

"""Translation rule for concurrent_requests feature."""

from typing import Dict, List
import click
from app2run.config.feature_config_loader import FeatureConfig, InputType, \
    get_feature_list_by_input_type
from app2run.common.util import flatten_keys, generate_output_flags, is_flex_env

_DEFAULT_STANDARD_CONCURRENCY = 10

def translate_concurrent_requests_features(input_data: Dict, \
    input_type: InputType, feature_config: FeatureConfig) -> List[str]:
    """Translate target_concurrent_requests(flex) and max_concurrent_requests
    (standard) to Cloud Run --concurrency flag."""

    input_key_value_pairs = flatten_keys(input_data, "")
    is_flex = is_flex_env(input_data)
    feature_key = _get_feature_key(is_flex)

    range_limited_features = get_feature_list_by_input_type(input_type, \
        feature_config.range_limited)
    feature = range_limited_features[feature_key]

    input_has_concurrent_requests = _has_concurrent_requests(input_key_value_pairs, \
        feature_key)
    if not input_has_concurrent_requests:
        default_value = feature.range['max'] if is_flex else \
            _DEFAULT_STANDARD_CONCURRENCY
        return generate_output_flags(feature.flags, default_value)

    input_value = input_key_value_pairs[feature_key]
    if input_value < feature.range['min']:
        click.echo(f'Warning: {feature_key} has invalid value of {input_value}, \
           minimum value is {feature.range["min"]}')
        return []
    target_value = input_value if \
        feature.is_within_range(input_value) else feature.range['max']
    return generate_output_flags(feature.flags, target_value)

def _has_concurrent_requests(input_key_value_pairs: Dict, feature_key: str) -> bool:
    return feature_key in input_key_value_pairs

def _get_feature_key(is_flex: bool) -> str:
    return 'automatic_scaling.target_concurrent_requests' if is_flex else \
        'automatic_scaling.max_concurrent_requests'
