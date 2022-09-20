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

"""Translation rule for app resources (instance_class, cpu, memory)."""
from typing import Dict, List
import click
from app2run.common.util import flatten_keys, get_features_by_prefix, is_flex_env, \
    generate_output_flags, get_feature_key_from_input
from app2run.commands.translation_rules.scaling import \
    ScalingTypeAppYaml, get_scaling_features_used

_ALLOWED_RESOURCE_KEY: List[str] = ['resources.cpu', 'resources.memory_gb']
_ALLOW_INSTANCE_CLASS_KEY: str = 'instance_class'
_DEFAULT_CPU_MEM_CONFIG: Dict = {
    ScalingTypeAppYaml.AUTOMATIC_SCALING: 'F1',
    ScalingTypeAppYaml.MANUAL_SCALING: 'B2',
    ScalingTypeAppYaml.BASIC_SCALING: 'B2'
}

# Cloud Run cpu unit can only specified to one of: 1.0, 2.0, 4.0, 6.0, 8.0
# See https://cloud.google.com/run/docs/configuring/cpu
# For 1.0 CPU, memory must be between 512Mi and 4Gi inclusive.
# For 4.0 CPU, memory must be between 2Gi and 16Gi inclusive.
# For 6.0 CPU, memory must be between 4Gi and 24Gi inclusive.
# See https://cloud.google.com/run/docs/configuring/memory-limits
_INSTANCE_CLASS_MAP : Dict = {
    'F1': {
        'cpu': 1,
        'memory': 0.5
    },
    'F2': {
        'cpu': 2,
        'memory': 0.5
    },
    'F4': {
        'cpu': 4,
        'memory': 2
    },
    'F4_1G': {
        'cpu': 4,
        'memory': 2
    },
    'B1': {
        'cpu': 1,
        'memory': 0.5
    },
    'B2': {
        'cpu': 2,
        'memory': 0.5
    },
    'B4': {
        'cpu': 4,
        'memory': 2
    },
    'B4_1G': {
        'cpu': 4,
        'memory': 2
    },
    'B8': {
        'cpu': 6,
        'memory': 4
    }
}
def translate_app_resources(input_data: Dict, range_limited_features: Dict) -> List[str]:
    """Translate instance_class(standard), cpu/memory(flex) to equivalent/compatible
    Cloud Run --cpu and --memory flags."""
    if is_flex_env(input_data):
        return _translate_flex_cpu_memory(input_data, range_limited_features)
    return _translate_standard_instance_class(input_data)

def _translate_flex_cpu_memory(input_data: Dict, range_limited_features: Dict) -> List[str]:
    output_flags: List[str] = []
    input_key_value_pairs = flatten_keys(input_data, "")
    input_feature_keys = get_features_by_prefix(input_key_value_pairs, 'resources')
    allowed_input_feature_keys = [key for key in input_feature_keys \
        if key in _ALLOWED_RESOURCE_KEY]
    for key in allowed_input_feature_keys:
        input_value = input_key_value_pairs[key]
        range_limited_feature = range_limited_features[key]
        target_value = input_value if range_limited_feature.is_within_range(input_value) \
            else range_limited_feature.range['max']
        field_name = key.split('.')[1]
        # Cloud Run --memory requires a unit suffix
        # https://cloud.google.com/run/docs/configuring/memory-limits#setting-services
        if field_name.startswith('memory'):
            target_value = _format_cloud_run_memory_unit(target_value)
        output_flags += generate_output_flags(range_limited_feature.flags, target_value)

    return output_flags

def _translate_standard_instance_class(input_data: Dict) -> List[str]:
    instance_class_key_from_input = get_feature_key_from_input(input_data, \
        [_ALLOW_INSTANCE_CLASS_KEY])
    if instance_class_key_from_input:
        instance_class = input_data[instance_class_key_from_input]
        return _generate_cpu_memory_flags_by_instance_class(instance_class)
    return _get_cpu_memory_default_based_on_scaling_method(input_data)

def _get_cpu_memory_default_based_on_scaling_method(input_data: Dict) \
    -> List[str]:
    scaling_features_used = get_scaling_features_used(input_data)
    if len(scaling_features_used) == 0:
        return []
    if len(scaling_features_used) > 1:
        click.echo('Warning: More than one scaling option is defined, \
            only one scaling option should be used.')
        return []
    scaling_method = scaling_features_used[0]
    default_instance_class = _DEFAULT_CPU_MEM_CONFIG[scaling_method]
    return _generate_cpu_memory_flags_by_instance_class(default_instance_class)

def _generate_cpu_memory_flags_by_instance_class(instance_class: str) -> List[str]:
    cpu_memory_config = _INSTANCE_CLASS_MAP[instance_class]
    cpu_value = cpu_memory_config["cpu"]
    memory_value = cpu_memory_config["memory"]
    # Cloud Run --memory requires a unit suffix
    # https://cloud.google.com/run/docs/configuring/memory-limits#setting-services
    memory_value = _format_cloud_run_memory_unit(memory_value)
    return [f'--cpu={cpu_value}', f'--memory={memory_value}']

def _format_cloud_run_memory_unit(value: float) -> str:
    # 1GB = 953Mi, 1Gi = 1024Mi memory, in Cloud Run, a minimum of 512MiB memory is
    # required for 1 CPU. Therefore, using Gi works for the lower bound of
    # memory requirement.
    # Allowed values are [m, k, M, G, T, Ki, Mi, Gi, Ti, Pi, Ei]
    return f'{value}Gi'
