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
from app2run.common.util import generate_output_flags, is_flex_env, \
    get_feature_key_from_input

_MAX_CONCURRENT_REQUESTS_KEY = 'automatic_scaling.max_concurrent_requests'
_TARGET_CONCURRENT_REQUESTS_KEY = 'automatic_scaling.target_concurrent_requests'
_ALLOW_MAX_CONCURRENT_REQ_KEYS = [_MAX_CONCURRENT_REQUESTS_KEY, _TARGET_CONCURRENT_REQUESTS_KEY]
_DEFAULT_STANDARD_CONCURRENCY = 10

def translate_concurrent_requests_features(input_data: Dict, \
    range_limited_features: Dict) -> List[str]:
    """Translate target_concurrent_requests(flex) and max_concurrent_requests
    (standard) to Cloud Run --concurrency flag."""
    is_flex = is_flex_env(input_data)
    feature_key = get_feature_key_from_input(input_data, \
        _ALLOW_MAX_CONCURRENT_REQ_KEYS)
    input_has_concurrent_requests = feature_key is not None

    # if input does not have max_concurrent_request/target_concurrent_request specified,
    # use the `automatic_scaling.max_concurrent_requests` from the app2run/config/features.yaml
    # as the default feature.
    if not input_has_concurrent_requests:
        feature = range_limited_features[_MAX_CONCURRENT_REQUESTS_KEY]
        default_value = feature.range['max'] if is_flex else \
            _DEFAULT_STANDARD_CONCURRENCY
        return generate_output_flags(feature.flags, default_value)

    feature = range_limited_features[feature_key]
    input_value = input_data[feature_key]
    if input_value < feature.range['min']:
        click.echo(f'Warning: {feature_key} has invalid value of {input_value}, \
           minimum value is {feature.range["min"]}')
        return []
    target_value = input_value if \
        feature.is_within_range(input_value) else feature.range['max']
    return generate_output_flags(feature.flags, target_value)
