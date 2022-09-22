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

"""Unit test for `app2run list-incompatible-features` command."""
from unittest.mock import patch
import os
from click.testing import CliRunner
from app2run.main import cli

runner = CliRunner()

##################### Tests using app.yaml input ###################

def test_appyaml_not_found():
    """test_appyaml_not_found"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['list-incompatible-features'])
        assert result.exit_code == 0
        assert "app.yaml does not exist in current directory, please use --appyaml flag \
to specify the app.yaml location.\n[Error] Failed to read input data.\n" \
            in result.output

def test_appyaml_empty():
    """test_appyaml_empty"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert result.output == "app.yaml is empty.\n[Error] Failed to read input data.\n"

def test_both_app_yaml_and_service_version_specified():
    """test_both_app_yaml_and_service_version_specified"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features', '--appyaml', 'app.yaml', \
                '--service', 'foo', '--version', 'bar'])
            assert result.exit_code == 0
            assert "[Error] Invalid input, only one of app.yaml or deployed version \
could be used as an input. Use --appyaml flag to specify the app.yaml, or use --service and --version \
to specify the deployed version." in result.output

def test_html_output_format_incompatibility_not_found():
    """test_html_output_format_incompatibility_not_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write('env: flex')
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features', '-o', 'html'])
            assert result.exit_code == 0
            assert result.output == "No incompatibilities found.\n"

def test_html_output_format_incompatibility_found():
    """test_html_output_format_incompatibility_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
beta_settings:
  cloud_sql_instances: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features', '-o', 'html'])
            assert result.exit_code == 0
            assert "Html output of incompatible features: /tmp/" in result.output

def test_appyaml_no_incompatibility_found():
    """test_appyaml_no_incompatibility_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write('env: flex')
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert result.output == "No incompatibilities found.\n"

def test_appyaml_beta_settings_cloud_sql_instances_unsupported():
    """test_appyaml_beta_settings_cloud_sql_instances_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
beta_settings:
  cloud_sql_instances: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: beta_settings.cloud_sql_instances" in result.output

def test_appyaml_volumes_unsupported():
    """test_appyaml_volumes_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
resources:
    volumes:
        - name: test
          volume_type: test
          size_gb: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: resources.volumes" in result.output

def test_appyaml_inbound_services_unsupported():
    """test_appyaml_inbound_services_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
inbound_services: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: inbound_services" in result.output

def test_appyaml_handlers_unsupported():
    """test_appyaml_handlers_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
handlers: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: handlers" in result.output

def test_appyaml_error_handlers_unsupported():
    """test_appyaml_error_handlers_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
error_handlers: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: error_handlers" in result.output

def test_appyaml_app_engine_apis_unsupported():
    """test_appyaml_app_engine_apis_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
app_engine_apis: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: app_engine_apis" in result.output

def test_appyaml_build_env_variables_unsupported():
    """test_appyaml_build_env_variables_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
build_env_variables: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: build_env_variables" in result.output

def test_appyaml_disk_size_gb_unsupported():
    """test_appyaml_disk_size_gb_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
resources:
    disk_size_gb: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: minor" in result.output
            assert "path: resources.disk_size_gb" in result.output

def test_appyaml_network_forwarded_ports_unsupported():
    """test_appyaml_network_forwarded_ports_unsupported"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
network:
  forwarded_ports: 80
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: network.forwarded_ports" in result.output

def test_appyaml_cpu_exceed_range_limited():
    """test_appyaml_cpu_exceed_range_limited"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
resources:
  cpu: 9
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: resources.cpu" in result.output

def test_appyaml_cpu_within_range_limited():
    """test_appyaml_cpu_within_range_limited"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
resources:
  cpu: 8
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert result.output == "No incompatibilities found.\n"

def test_appyaml_memory_exceed_range_limited():
    """test_appyaml_memory_exceed_range_limited"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
resources:
  memory_gb: 33
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: resources.memory_gb" in result.output

def test_appyaml_memory_within_range_limited():
    """test_appyaml_memory_within_range_limited"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
resources:
  memory_gb: 32
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert result.output == "No incompatibilities found.\n"

def test_appyaml_runtime_config_python_version_2_value_limited():
    """test_appyaml_runtime_config_python_version_2_value_limited"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime_config:
  python_version: 2
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: runtime_config.python_version" in result.output

def test_appyaml_runtime_config_python_version_3_value_limited():
    """test_appyaml_runtime_config_python_version_3_value_limited"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime_config:
  python_version: 3
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert result.output == "No incompatibilities found.\n"

def test_appyaml_runtime_config_unknonw_value_limited():
    """test_appyaml_runtime_config_unknonw_value_limited"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime_config:
  python_version: 4
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "path: runtime_config.python_version" in result.output
            assert "severity: unknown" in result.output
            assert "4 is not a known value for runtime_config.python_version" in result.output

##################### Tests using deployed version (admin API) input ###################

def test_admin_api_no_incompatibility_found():
    """test_admin_api_no_incompatibility_found"""
    gcloud_version_describe_output = """
env: flex
id: dummy-python
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert 'No incompatibilities found.' in result.output

def test_admin_api_beta_settings_cloud_sql_instances_unsupported():
    """test_admin_api_beta_settings_cloud_sql_instances_unsupported"""
    gcloud_version_describe_output = """
betaSettings:
  cloudSqlInstances: test
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: betaSettings.cloudSqlInstances" in result.output
        assert "reason: Cloud Run does not support TCP based CloudSQL instance configs." \
            in result.output

def test_admin_api_volumes_unsupported():
    """test_admin_api_volumes_unsupported"""
    gcloud_version_describe_output = """
resources:
    volumes:
        - name: test
          volumeType: test
          sizeGb: 1
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: resources.volumes" in result.output
        assert "reason: Cloud Run does not support tmpfs volume mounts." in result.output

def test_admin_api_handlers_unsupported():
    """test_admin_api_handlers_unsupported"""
    gcloud_version_describe_output = """
handlers:
- authFailAction: AUTH_FAIL_ACTION_REDIRECT
  login: LOGIN_OPTIONAL
  script:
    scriptPath: main.root
  securityLevel: SECURE_OPTIONAL
  urlRegex: /
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: handlers" in result.output
        assert 'reason: No support for routing based on url patterns' in result.output

def test_admin_api_inbound_services_unsupported():
    """test_admin_api_inbound_services_unsupported"""
    gcloud_version_describe_output = """
inboundServices: test
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: inboundServices" in result.output
        assert 'reason: Cloud Run does not support GAE bundled services.' in result.output

def test_admin_api_error_handlers_unsupported():
    """test_admin_api_error_handlers_unsupported"""
    gcloud_version_describe_output = """
errorHandlers: test
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: errorHandlers" in result.output
        assert 'reason: No support for routing based on url patterns.' in result.output

def test_admin_api_app_engine_apis_unsupported():
    """test_admin_api_app_engine_apis_unsupported"""
    # caplog.set_level(logging.INFO)
    gcloud_version_describe_output = """
appEngineApis: test
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: appEngineApis" in result.output
        assert 'reason: No App Engine bundled services.' in result.output

def test_admin_api_build_env_variables_unsupported():
    """test_admin_api_build_env_variables_unsupported"""
    gcloud_version_describe_output = """
buildEnvVariables: test
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: buildEnvVariables" in result.output
        assert 'reason: No support for passing environment vars to \
buildpacks at the time of building.' in result.output

def test_admin_api_disk_size_gb_unsupported():
    """test_admin_api_disk_size_gb_unsupported"""
    gcloud_version_describe_output = """
resources:
    diskGb: 1
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: minor" in result.output
        assert "path: resources.diskGb" in result.output
        assert 'reason: No support for custom disk size.' in result.output

def test_admin_api_network_forwarded_ports_unsupported():
    """test_admin_api_network_forwarded_ports_unsupported"""
    gcloud_version_describe_output = """
network:
  forwardedPorts: 80
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: network.forwardedPorts" in result.output
        assert 'reason: Cloud Run does not support port forwarding. \
No clients can connect to the\n    app using the forwarded ports.' in result.output

def test_admin_api_cpu_exceed_range_limited():
    """test_admin_api_cpu_exceed_range_limited"""
    gcloud_version_describe_output = """
resources:
  cpu: 9
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: resources.cpu" in result.output
        assert 'reason: Cloud Run supports max 8 CPUs.' in result.output

def test_admin_api_cpu_within_range_limited():
    """test_admin_api_cpu_within_range_limited"""
    gcloud_version_describe_output = """
resources:
  cpu: 8
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert result.output == "No incompatibilities found.\n"

def test_admin_api_memory_exceed_range_limited():
    """test_admin_api_memory_exceed_range_limited"""
    gcloud_version_describe_output = """
resources:
  memoryGb: 33
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: resources.memoryGb" in result.output
        assert 'reason: Cloud Run supports max 32Gi of memory.' in result.output

def test_admin_api_memory_within_range_limited():
    """test_admin_api_memory_within_range_limited"""
    gcloud_version_describe_output = """
resources:
  memoryGb: 32
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert result.output == "No incompatibilities found.\n"

def test_admin_api_runtime_config_python_version_2_value_limited():
    """test_admin_api_runtime_config_python_version_2_value_limited"""
    gcloud_version_describe_output = """
runtimeConfig:
  pythonVersion: 2
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: major" in result.output
        assert "path: runtimeConfig.pythonVersion" in result.output
        assert 'reason: Cloud Run supports Python 3 runtime only.' in result.output

def test_admin_api_runtime_config_python_version_3_value_limited():
    """test_admin_api_runtime_config_python_version_3_value_limited"""
    gcloud_version_describe_output = """
runtimeConfig:
  pythonVersion: 3
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert result.output == "No incompatibilities found.\n"

def test_admin_api_runtime_config_unknonw_value_limited():
    """test_admin_api_runtime_config_unknonw_value_limited"""
    gcloud_version_describe_output = """
runtimeConfig:
  pythonVersion: 4
"""
    with patch.object(os, 'popen', return_value=gcloud_version_describe_output) as mock_popen:
        result = runner.invoke(cli, \
            ['list-incompatible-features', '--service', 'foo', '--version', 'bar'])
        mock_popen.assert_called_with('gcloud app versions describe bar --service=foo')
        assert result.exit_code == 0
        assert "major: 1" in result.output
        assert "incompatible_features" in result.output
        assert "severity: unknown" in result.output
        assert "path: runtimeConfig.pythonVersion" in result.output
        assert 'reason: 4 is not a known value for runtimeConfig.pythonVersion' in result.output
