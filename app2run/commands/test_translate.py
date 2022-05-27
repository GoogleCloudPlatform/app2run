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
            expected_flags = "--min-instances=1\n"
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
            expected_flags = "--max-instances=999\n"
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
            expected_flags = "--max-instances=1000\n"
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
            expected_flags = "--min-instances=1\n"
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
            expected_flags = "--max-instances=999\n"
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
            expected_flags = "--max-instances=1000\n"
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
            expected_flags = "--concurrency=10\n"
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
