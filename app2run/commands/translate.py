"""translate module contains the implmentation for the `app2run translate` command.
"""

from typing import Dict, List
import click
import yaml
from app2run.config.feature_config_loader import InputType, FeatureConfig,\
    get_feature_config
from app2run.commands.translation_rules.scaling import translate_scaling_features
from app2run.commands.translation_rules.concurrent_requests import \
    translate_concurrent_requests_features
from app2run.commands.translation_rules.timeout import translate_timeout_features
from app2run.commands.translation_rules.cpu_memory import translate_app_resources
from app2run.commands.translation_rules.supported_features import translate_supported_features
from app2run.commands.translation_rules.required_flags import translate_add_required_flags

@click.command(short_help="Translate an app.yaml to migrate to Cloud Run.")
@click.option('-a', '--appyaml', default='app.yaml', show_default=True, \
    help='Path to the app.yaml of the app.', type=click.File())
@click.option('-p', '--project', help="The project id to deploy the Cloud Run app.")
@click.option('-s', '--service-name', help="The name of the service for the Cloud Run app.")
def translate(appyaml, project, service_name) -> None:
    """Translate command translates app.yaml to eqauivalant gcloud command to migrate the \
        GAE App to Cloud Run."""
    input_data = yaml.safe_load(appyaml.read())
    if input_data is None:
        click.echo(f'{appyaml.name} is empty.')
        return

    flags: List[str] = _get_cloud_run_flags(input_data, InputType.APP_YAML, project)
    service_name = service_name if service_name is not None else _get_service_name(input_data)
    _generate_output(service_name, flags)

def _get_cloud_run_flags(input_data: Dict, input_type: InputType, project: str):
    feature_config : FeatureConfig = get_feature_config()
    return translate_concurrent_requests_features(input_data, input_type, feature_config) + \
           translate_scaling_features(input_data, input_type, feature_config) + \
           translate_timeout_features(input_data) + \
           translate_app_resources(input_data, input_type) + \
           translate_supported_features(input_data, input_type, project) + \
           translate_add_required_flags()

def _get_service_name(input_data: Dict):
    if 'service' in input_data:
        custom_service_name = input_data['service'].strip()
        if len(custom_service_name) > 0:
            return custom_service_name
    return 'default'

def _generate_output(service_name: str, flags: List[str]):
    """
    example output:
    gcloud beta run deploy default \
      --cpu=1 \
      --memory=2Gi \
      --timeout=10m
    """
    click.echo("""Warning:not all configuration could be translated,
for more info use app2run list–incompatible-features.""")
    first_line_ending_char = '' if flags is None or len(flags) == 0 else '\\'
    output = f"""
gcloud beta run deploy {service_name} {first_line_ending_char}
"""
    if flags is not None:
        for i, flag in enumerate(flags):
            # The last flag does not have tailing \
            output += '  '
            output += flag + ' \\' if i < len(flags) - 1 else flag
            output += '\n'
    click.echo(output)
