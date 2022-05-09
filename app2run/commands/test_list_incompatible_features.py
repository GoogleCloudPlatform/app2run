
"""Unit test for `app2run list-incompatible-features` command."""
from click.testing import CliRunner
from app2run.main import cli

runner = CliRunner()

def test_appyaml_not_found():
    """test_appyaml_not_found"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['list-incompatible-features'])
        assert result.exit_code == 2
        assert "Error: Invalid value for '-a' / '--appyaml': 'app.yaml': No such file or director" \
            in result.output

def test_appyaml_empty():
    """test_appyaml_empty"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert result.output == "app.yaml is empty.\n"

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
volumes: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: major" in result.output
            assert "path: volumes" in result.output

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
disk_size_gb: test
            """)
            appyaml.close()
            result = runner.invoke(cli, ['list-incompatible-features'])
            assert result.exit_code == 0
            assert "major: 1" in result.output
            assert "incompatible_features" in result.output
            assert "severity: minor" in result.output
            assert "path: disk_size_gb" in result.output

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
    """test_appyaml_runtime_config_python_version_3_value_limited"""
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
