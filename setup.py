"""Setup file for app2run package."""
from setuptools import setup, find_packages

setup(
    name='app2run',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'Click',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'app2run = app2run.main:cli',
        ],
    },
)
