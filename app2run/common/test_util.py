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

"""Unit tests for util.py."""

from app2run.common.util import generate_output_flags, is_flex_env, get_feature_key_from_input

def test_flex_env_app_yaml():
    """test_flex_env_app_yaml"""
    input_data = {
        'env': 'flex'
    }
    output = is_flex_env(input_data)
    assert output is True

def test_standard_env_app_yaml():
    """test_standard_env_app_yaml"""
    input_data = {}
    output = is_flex_env(input_data)
    assert output is False

def test_flex_env_admin_api():
    """test_flex_env_admin_api"""
    input_data = {
        'env': 'flexible'
    }
    output = is_flex_env(input_data)
    assert output is True

def test_generate_output_flags_single_flag():
    """test_generate_output_flags_single_flag"""
    flags = ['--a']
    value = 'b'
    output = generate_output_flags(flags, value)
    assert output == ['--a=b']

def test_generate_output_flags_multi_flags():
    """test_generate_output_flags_multi_flags"""
    flags = ['--a', '--b']
    value = 'c'
    output = generate_output_flags(flags, value)
    assert output == ['--a=c', '--b=c']

def test_get_feature_key_from_input_one_key_detected():
    """test_get_feature_key_from_input"""
    input_data = {
        'key1', 'value1',
        'key2', 'value2'
    }
    allow_keys = ['key1']
    output = get_feature_key_from_input(input_data, allow_keys)
    assert output == 'key1'

def test_get_feature_key_from_input_no_key_detected():
    """test_get_feature_key_from_input"""
    input_data = {
        'key1', 'value1',
        'key2', 'value2'
    }
    allow_keys = ['key3']
    output = get_feature_key_from_input(input_data, allow_keys)
    assert output is None

def test_get_feature_key_from_input_multiple_keys_detected():
    """test_get_feature_key_from_input"""
    input_data = {
        'key1', 'value1',
        'key2', 'value2'
    }
    allow_keys = ['key1', 'key2']
    output = get_feature_key_from_input(input_data, allow_keys)
    assert output is None
