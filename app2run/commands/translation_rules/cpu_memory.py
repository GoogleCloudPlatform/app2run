"""Translation rule for app resources (instance_class, cpu, memory)."""

from typing import Dict, List
import click
from app2run.common.util import flatten_keys, get_features_by_prefix, is_flex_env, \
    generate_output_flags
from app2run.commands.translation_rules.scaling import get_scaling_features_used
from app2run.config.feature_config_loader import FeatureConfig, InputType, \
    get_feature_config, get_feature_list_by_input_type

_ALLOWED_RESOURCE_KEY: List[str] = ['cpu', 'memory_gb', 'memoryGb']

_DEFAULT_CPU_MEM_CONFIG: Dict = {
    'automatic_scaling': 'F1',
    'manual_scaling': 'B2',
    'basic_scaling': 'B2'
}

_INSTANCE_CLASS_MAP : Dict = {
    'F1': {
        'cpu': 1,
        'memory': 0.25
    },
    'F2': {
        'cpu': 1.2,
        'memory': 0.5
    },
    'F4': {
        'cpu': 2.4,
        'memory': 1
    },
    'F4_1G': {
        'cpu': 2.4,
        'memory': 2
    },
    'B1': {
        'cpu': 1,
        'memory': 0.25
    },
    'B2': {
        'cpu': 1.2,
        'memory': 0.5
    },
    'B4': {
        'cpu': 2.4,
        'memory': 1
    },
    'B4_1G': {
        'cpu': 2.4,
        'memory': 2
    },
    'B8': {
        'cpu': 4.8,
        'memory': 2
    }
}
def translate_app_resources(input_data: Dict, input_type: InputType) -> List[str]:
    """Translate instance_class(standard), cpu/memory(flex) to equivalent/compatible
    Cloud Run --cpu and --memory flags."""
    if is_flex_env(input_data):
        return _translate_flex_cpu_memory(input_data, input_type)
    return _translate_standard_instance_class(input_data)

def _translate_flex_cpu_memory(input_data: Dict, input_type: InputType) -> List[str]:
    output_flags: List[str] = []
    feature_config : FeatureConfig = get_feature_config()
    range_limited_features =  get_feature_list_by_input_type(input_type, \
    feature_config.range_limited)

    input_key_value_pairs = flatten_keys(input_data, "")
    input_feature_keys = get_features_by_prefix(input_key_value_pairs, 'resources')
    allowed_input_feature_keys = [key for key in input_feature_keys \
        if key.split('.')[1] in _ALLOWED_RESOURCE_KEY]
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
    if 'instance_class' in input_data:
        instance_class = input_data['instance_class']
        return _generate_cpu_memory_flags_by_instance_class(instance_class)
    return _get_cpu_memory_default_based_on_scaling_method(input_data)

def _get_cpu_memory_default_based_on_scaling_method(input_data: Dict) -> List[str]:
    scaling_features_used = get_scaling_features_used(input_data)
    if len(scaling_features_used) == 0:
        return []
    if len(scaling_features_used) > 1:
        click.echo('Warning: More than one scaling option is defined, \
            only one scaling option should be used.')
        return []
    scaling_method = scaling_features_used[0]
    default_instance_class = _DEFAULT_CPU_MEM_CONFIG[scaling_method.value]
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
    # 1G = 953Mi, 1Gi = 1024Mi memory, in Cloud Run, a minimum of 512Mi memory is
    # required for 1 CPU. Therefore, using Gi works for the lower bound of
    # memory requirement.
    return f'{value}Gi'
