"""Unit tests for util.py."""
from app2run.common.util import generate_output_flags

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
