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

"""Translation rule for timeout feature."""

from typing import Dict, List
from app2run.common.util import is_flex_env
from app2run.commands.translation_rules.scaling import \
    ScalingTypeAppYaml, get_scaling_features_used

_SCALING_METHOD_W_10_MIN_TIMEOUT = {
    ScalingTypeAppYaml.AUTOMATIC_SCALING
}
_SCALING_METHOD_W_60_MIN_TIMEOUT = {
    ScalingTypeAppYaml.MANUAL_SCALING,
    ScalingTypeAppYaml.BASIC_SCALING
}

def translate_timeout_features(input_data: Dict) -> List[str]:
    """Tranlsate default timeout values for setting the --timeout flag to Cloud Run."""
    is_flex = is_flex_env(input_data)

    if is_flex:
        return ['--timeout=60m']

    scaling_features_used = get_scaling_features_used(input_data)

    if len(scaling_features_used) == 1:
        scaling_feature = scaling_features_used[0]
        if scaling_feature in _SCALING_METHOD_W_10_MIN_TIMEOUT:
            return ['--timeout=10m']
        if scaling_feature in _SCALING_METHOD_W_60_MIN_TIMEOUT:
            return ['--timeout=60m']
    return []
