"""This module contains common utility functions."""

from typing import Dict, List, Any

def is_flex_env(input_data: Dict) -> bool:
    """Detect whether input app.yaml is for flex environment."""
    return 'env' in input_data and input_data['env'] == 'flex'

def generate_output_flags(flags: List[str], value: str) -> List[str]:
    """Generate output flags by given list of flag names and value."""
    output_flags: List[str] = []
    for flag in flags:
        output_flags.append(f'{flag}={value}')
    return output_flags

def get_features_by_prefix(features: Dict, prefix: str) -> Dict:
    """Return a list of features matched with the prefix."""
    matched_features: Dict = {}
    for feature_key in features:
        if feature_key.startswith(prefix):
            matched_features[feature_key] = features[feature_key]
    return matched_features

def flatten_keys(input_data: Dict, parent_path: str) -> Dict[str, Any]:
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
            paths.update(flatten_keys(input_data[key], curr_path))
    return paths
