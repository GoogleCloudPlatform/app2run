"""Unit test for `app2run translate` command."""
from click.testing import CliRunner
from app2run.main import cli

runner = CliRunner()

def test_appyaml_not_found():
    """test_appyaml_not_found"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['translate'])
        assert result.exit_code == 2
        assert "Error: Invalid value for '-a' / '--appyaml': 'app.yaml': No such file or director" \
            in result.output

def test_appyaml_empty():
    """test_appyaml_empty"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            assert result.exit_code == 0
            assert result.output == "app.yaml is empty.\n"

def test_default_service_name():
    """test_default_service_name"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_output = "gcloud run deploy default"
            assert expected_output in result.output

def test_custom_service_name():
    """test_custom_service_name"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
service: test_service_name
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_output = "gcloud run deploy test_service_name"
            assert expected_output in result.output

def test_standard_when_no_scaling_feature_found():
    """test_standard_when_no_scaling_feature_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime: python
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_flags = """--min-instances=0 \\
  --max-instances=1000"""
            assert unexpected_flags not in result.output

def test_standard_automatic_scaling_with_valid_min():
    """test_standard_automatic_scaling_with_valid_min"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    min_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--min-instances=1 "
            assert expected_flags in result.output

def test_standard_automatic_scaling_with_invalid_min_value():
    """test_standard_automatic_scaling_with_invalid_min_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    min_instances: -1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_flags = "--min-instances\n"
            assert unexpected_flags not in result.output

def test_standard_automatic_scaling_with_valid_max_value():
    """test_standard_automatic_scaling_with_valid_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    max_instances: 999
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--max-instances=999 "
            assert expected_flags in result.output

def test_standard_automatic_scaling_with_invalid_max_value():
    """test_standard_automatic_scaling_with_invalid_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    max_instances: 1001
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--max-instances=1000 "
            assert expected_flags in result.output

def test_flex_when_no_scaling_feature_found():
    """test_flex_when_no_scaling_feature_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_flags = """--min-instances=0 \\
  --max-instances=1000"""
            assert unexpected_flags not in result.output

def test_flex_automatic_scaling_with_valid_min_value():
    """test_flex_automatic_scaling_with_valid_min_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    min_num_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--min-instances=1 "
            assert expected_flags in result.output

def test_flex_automatic_scaling_with_invalid_min_value():
    """test_flex_automatic_scaling_with_invalid_min_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    min_num_instances: -1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_flags = "--min-instances\n"
            assert unexpected_flags not in result.output

def test_flex_automatic_scaling_with_valid_max_value():
    """test_automatic_scaling_with_valid_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    max_num_instances: 999
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--max-instances=999 "
            assert expected_flags in result.output

def test_flex_automatic_scaling_with_invalid_max_value():
    """test_automatic_scaling_with_invalid_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    max_num_instances: 1001
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--max-instances=1000 "
            assert expected_flags in result.output

def test_manual_scaling_with_valid_instances_value():
    """test_manual_scaling_with_valid_instances_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
manual_scaling:
   instances: 10
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = """--min-instances=10 \\
  --max-instances=10"""
            assert expected_flags in result.output

def test_manual_scaling_with_invalid_instances_value():
    """test_manual_scaling_with_invalid_instances_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
manual_scaling:
   instances: 1001
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = """--min-instances=1000 \\
  --max-instances=1000"""
            assert expected_flags in result.output

def test_basic_scaling_with_valid_instances_value():
    """test_basic_scaling_with_valid_instances_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
basic_scaling:
   max_instances: 10
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = """--min-instances=10 \\
  --max-instances=10"""
            assert expected_flags in result.output

def test_basic_scaling_with_invalid_instances_value():
    """test_basic_scaling_with_invalid_instances_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
basic_scaling:
   max_instances: 1001
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = """--min-instances=1000 \\
  --max-instances=1000"""
            assert expected_flags in result.output

def test_flex_target_concurrent_automatic_scaling_not_specified():
    """test_flex_target_concurrent_automatic_scaling_not_specified"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=1000"
            assert expected_flags in result.output

def test_flex_target_concurrent_requests_not_specified():
    """test_flex_target_concurrent_requests_not_specified"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    min_num_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=1000"
            assert expected_flags in result.output

def test_flex_target_concurrent_requests_specified_within_max_value():
    """test_flex_target_concurrent_requests_specified_within_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    target_concurrent_requests: 999
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=999"
            assert expected_flags in result.output

def test_flex_target_concurrent_requests_specified_gt_max_value():
    """test_flex_target_concurrent_requests_specified_gt_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    target_concurrent_requests: 1001
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=1000"
            assert expected_flags in result.output

def test_flex_target_concurrent_requests_invalid_value():
    """test_flex_target_concurrent_requests_invalid_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
automatic_scaling:
    target_concurrent_requests: 0
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_flags = "--concurrency"
            assert unexpected_flags not in result.output

def test_standard_max_concurrent_automatic_scaling_not_specified():
    """test_standard_max_concurrent_automatic_scaling_not_specified"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime: python
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=10 "
            assert expected_flags in result.output

def test_standard_max_concurrent_requests_not_specified():
    """test_standard_max_concurrent_requests_not_specified"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    min_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=10 "
            assert expected_flags in result.output

def test_standard_max_concurrent_requests_specified_within_max_value():
    """test_standard_max_concurrent_requests_specified_within_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    max_concurrent_requests: 999
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=999"
            assert expected_flags in result.output

def test_standard_max_concurrent_requests_specified_gt_max_value():
    """test_standard_max_concurrent_requests_specified_gt_max_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    max_concurrent_requests: 1001
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--concurrency=1000"
            assert expected_flags in result.output

def test_standard_max_concurrent_requests_invalid_value():
    """test_standard_max_concurrent_requests_invalid_value"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    max_concurrent_requests: 0
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_flags = "--concurrency"
            assert unexpected_flags not in result.output
def test_timeout_flex_env():
    """test_timeout_flex_env"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--timeout=60m"
            assert expected_flags in result.output

def test_timeout_standard_env_no_scaling_feature():
    """test_timeout_standard_env_no_scaling_feature"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime: python
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_flags = "--timeout"
            assert unexpected_flags not in result.output

def test_timeout_standard_env_automatic_scaling():
    """test_timeout_standard_env_automatic_scaling"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    min_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--timeout=10m"
            assert expected_flags in result.output

def test_timeout_standard_env_manual_scaling():
    """test_timeout_standard_env_manual_scaling"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
manual_scaling:
    instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--timeout=60m"
            assert expected_flags in result.output

def test_timeout_standard_env_basic_scaling():
    """test_timeout_standard_env_basic_scaling"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
basic_scaling:
    max_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flags = "--timeout=60m"
            assert expected_flags in result.output

def test_cpu_memory_standard_instance_class_not_specified():
    """test_cpu_memory_standard_instance_class_not_specified"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime: python
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_cpu_flag = "--cpu="
            unexpected_memory_flag = "--memory"
            assert unexpected_cpu_flag not in result.output
            assert unexpected_memory_flag not in result.output

def test_cpu_memory_standard_automatic_scaling_default():
    """test_cpu_memory_standard_automatic_scaling_default"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
automatic_scaling:
    min_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=1"
            expected_memory_flag = "--memory=0.25Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_manual_scaling_default():
    """test_cpu_memory_standard_manual_scaling_default"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
manual_scaling:
    instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=1.2"
            expected_memory_flag = "--memory=0.5Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_basic_scaling_default():
    """test_cpu_memory_standard_basic_scaling_default"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
basic_scaling:
    max_instances: 1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=1.2"
            expected_memory_flag = "--memory=0.5Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_f1():
    """test_cpu_memory_standard_instance_class_f1"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: F1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=1"
            expected_memory_flag = "--memory=0.25Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_f2():
    """test_cpu_memory_standard_instance_class_f2"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: F2
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=1.2"
            expected_memory_flag = "--memory=0.5Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_f4():
    """test_cpu_memory_standard_instance_class_f4"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: F4
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=2.4"
            expected_memory_flag = "--memory=1Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_f4_1g():
    """test_cpu_memory_standard_instance_class_f4_1g"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: F4_1G
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=2.4"
            expected_memory_flag = "--memory=2Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_b1():
    """test_cpu_memory_standard_instance_class_b1"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: B1
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=1"
            expected_memory_flag = "--memory=0.25Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_b2():
    """test_cpu_memory_standard_instance_class_b2"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: B2
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=1.2"
            expected_memory_flag = "--memory=0.5Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_b4():
    """test_cpu_memory_standard_instance_class_b4"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: B4
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=2.4"
            expected_memory_flag = "--memory=1Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_b4_1g():
    """test_cpu_memory_standard_instance_class_b4_1g"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: B4_1G
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=2.4"
            expected_memory_flag = "--memory=2Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_standard_instance_class_b8():
    """test_cpu_memory_standard_instance_class_b8"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
instance_class: B8
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=4.8"
            expected_memory_flag = "--memory=2Gi"
            assert expected_cpu_flag in result.output
            assert expected_memory_flag in result.output

def test_cpu_memory_flex_cpu_memory_not_specified():
    """test_cpu_memory_flex_cpu_memory_not_specified"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_cpu_flag = "--cpu="
            unexpected_memory_flag = "--memory"
            assert unexpected_cpu_flag not in result.output
            assert unexpected_memory_flag not in result.output

def test_cpu_memory_flex_cpu_specified_lt_max():
    """test_cpu_memory_flex_cpu_specified_lt_max"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
resources:
    cpu: 7
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=7"
            assert expected_cpu_flag in result.output

def test_cpu_memory_flex_cpu_specified_gt_max():
    """test_cpu_memory_flex_cpu_specified_gt_max"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
resources:
    cpu: 9
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_cpu_flag = "--cpu=8"
            assert expected_cpu_flag in result.output

def test_cpu_memory_flex_memory_gb_specified_lt_max():
    """test_cpu_memory_flex_memory_gb_specified_lt_max"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
resources:
    memory_gb: 31
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_memory_flag = "--memory=31Gi"
            assert expected_memory_flag in result.output

def test_cpu_memory_flex_memory_gb_specified_gt_max():
    """test_cpu_memory_flex_memory_gb_specified_gt_max"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env: flex
resources:
    memory_gb: 33
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_memory_flag = "--memory=32Gi"
            assert expected_memory_flag in result.output

def test_entrypoint_found():
    """test_entrypoint"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
entrypoint: foo
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flag = "--command=\"foo\""
            assert expected_flag in result.output

def test_env_variables_found():
    """test_env_variables_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
env_variables:
    foo: bar
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flag = "--set-env-vars=\"foo=bar\""
            assert expected_flag in result.output

def test_vpc_access_connector_name_found():
    """test_vpc_access_connector_name_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
vpc_access_connector:
    name: foo
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flag = "--vpc-connector=\"foo\""
            assert expected_flag in result.output

def test_vpc_access_connector_egress_settings_found():
    """test_vpc_access_connector_egress_settings_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
vpc_access_connector:
    egress_settings: foo
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flag = "--vpc-egress=\"foo\""
            assert expected_flag in result.output

def test_service_account_found():
    """test_service_account_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
service_account: foo@bar.com
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            expected_flag = "--service-account=\"foo@bar.com\""
            assert expected_flag in result.output

def test_service_account_not_found_project_flag_specified_cli():
    """test_service_account_not_found_project_flag_specified_cli"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime: python
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate', '-p', 'test'])
            expected_flag = "--service-account=test@appspot.gserviceaccount.com"
            assert expected_flag in result.output

def test_supported_features_not_found():
    """test_supported_features_not_found"""
    with runner.isolated_filesystem():
        with open('app.yaml', 'w', encoding='utf8') as appyaml:
            appyaml.write("""
runtime: python
            """)
            appyaml.close()
            result = runner.invoke(cli, ['translate'])
            unexpected_command_flag = "--command"
            unexpected_set_env_vars_flag="--set-env-vars"
            unexpected_vpc_connector_flag="--vpc-connector"
            unexpected_vpc_egress_flag="--vpc-egress"
            assert unexpected_command_flag not in result.output
            assert unexpected_set_env_vars_flag not in result.output
            assert unexpected_vpc_connector_flag  not in result.output
            assert unexpected_vpc_egress_flag not in result.output
