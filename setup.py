""" See <https://setuptools.readthedocs.io/en/latest/>.
"""
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """ Custom class to avoid depending on pytest-runner.
    """
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    version='0.1.1',
    name='datapunt-oauth2',
    description="Permission Management and OAuth2 Authorization Service",
    # long_description="",
    url='https://github.com/DatapuntAmsterdam/oauth2',
    author='Amsterdam Datapunt',
    author_email='datapunt.ois@amsterdam.nl',
    license='Mozilla Public License Version 2.0',
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass={'test': PyTest},
    packages=['oauth2'],
    install_requires=[
        'jsonschema',
        'psycopg2',
        'pyyaml',
        'sqlalchemy',
        'aiohttp==2.0.7'
    ],
    extras_require={
        'doc': [
            'sphinx',
            'sphinx_rtd_theme'
        ],
        'dev': [],
    },
    tests_require=['pytest==3.0.5', 'pytest-cov==2.4.0'],
)
