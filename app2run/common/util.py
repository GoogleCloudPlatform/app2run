"""This module contains common utility functions."""

import os
from typing import Dict, List, Any, Tuple
import click
import yaml
from app2run.config.feature_config_loader import InputType

ENTRYPOINT_FEATURE_KEYS: List[str] = ['entrypoint', 'entrypoint.shell']
# Entrypoint for these runtimes must be specified in a Procfile
# instead of via the `--command` flag at the gcloud run deploy
# command.
RUNTIMES_WITH_PROCFILE_ENTRYPOINT: List[str] = ['python', 'ruby']
_ALLOW_FLEX_ENV_VALUES = ['flex', 'flexible']
_FLATTEN_EXCLUDE_KEYS = ['env_variables', 'envVariables']

def is_flex_env(input_data: Dict) -> bool:
    """Detect whether input app.yaml is for flex environment."""
    return 'env' in input_data and input_data['env'] in _ALLOW_FLEX_ENV_VALUES

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
        if not isinstance(input_data[key], dict) or key in _FLATTEN_EXCLUDE_KEYS:
            paths[curr_path] = input_data[key]
        else:
            paths.update(flatten_keys(input_data[key], curr_path))
    return paths

def validate_input(appyaml, service, version, project) -> Tuple[InputType, Dict]:
    """Validate the input for cli commands. Either app.yaml or deployed version \
        could be used as an input at any given time. Return the input type and \
        input data (as python objects) if validation passes."""
    # `app2run translate --appyaml=XXX --service=XXX --version=XXX` is invalid, because
    # both appyaml and deployed version are specified.
    appyaml_param_specified = appyaml is not None
    deployed_version_specified = service is not None and version is not None
    if appyaml_param_specified and deployed_version_specified:
        click.echo("[Error] Invalid input, only one of app.yaml or deployed version could be \
used as an input. Use --appyaml flag to specify the app.yaml, or use --service and --version \
to specify the deployed version.")
        return (None, None)
    # If user runs `app2run translate` without providing any parameters, it assumes the \
    # current directory has an `app.yaml` file by default.
    if not deployed_version_specified and not appyaml_param_specified:
        appyaml = 'app.yaml'
    input_type = InputType.ADMIN_API if deployed_version_specified else InputType.APP_YAML
    input_data = get_input_data_by_input_type(input_type, appyaml, service, version, project)
    if input_data is None:
        click.echo('[Error] Failed to read input data.')
    return (input_type, input_data)

def get_input_data_by_input_type(input_type: InputType, appyaml, service=None, \
    version=None, project=None) -> Dict:
    """Retrieve the input_data (from yaml to python objects) by a given input_type."""
    # deployed version is input type
    if input_type == InputType.ADMIN_API:
        gcloud_command = f'gcloud app versions describe {version} --service={service}'
        if project is not None:
            gcloud_command += f' --project={project}'
        gcloud_output = os.popen(gcloud_command)
        return yaml.safe_load(gcloud_output)

    # appyaml is input type
    try:
        with open(appyaml, 'r', encoding='utf8') as file:
            appyaml_data = yaml.safe_load(file.read())
            if appyaml_data is None:
                click.echo(f'{file.name} is empty.')
            return appyaml_data
    except IOError:
        click.echo('app.yaml does not exist in current directory, please use --appyaml flag \
to specify the app.yaml location.')
    return None

def get_feature_key_from_input(input_key_value_pairs: Dict, allow_keys: List[str]) -> str:
    """Get feature key from input based on list of allowed keys."""
    allow_keys_from_input = [key for key in input_key_value_pairs if key in allow_keys]
    if len(allow_keys_from_input) == 0:
        return None
    if len(allow_keys_from_input) > 1:
        click.echo(f'[Error] Conflicting configurations found: {allow_keys_from_input}. \
Please ensure only one is specified".')
        return None
    return allow_keys_from_input[0]
