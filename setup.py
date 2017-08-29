#!/usr/bin/env python3

"""See <https://setuptools.readthedocs.io/en/latest/>.
"""
from setuptools import setup
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
    packages=['oauth2', 'config_loader', 'rest_utils'],
    install_requires=[
        'aiodns', # Recommended by aiohttp docs
        'aiohttp',
        'aiohttp-jinja2',
        'aiopg',
        'alembic',
        'cchardet', # Recommended by aiohttp docs
        'docutils',
        'jsonschema',
        'mimeparse',
        'PyYaml',
        'PyJWT',
        'SQLAlchemy',
        'swagger-parser',
        'uvloop', # Recommended by aiohttp docs
    ],
    extras_require={
        'docs': [
            'MacFSEvents',
            'Sphinx',
            'sphinx-autobuild',
            'sphinx_rtd_theme',
        ],
        'test': [
            'pytest',
            'pytest-cov',
        ],
        'dev': [
            'jupyter',
            'aiohttp-devtools'
        ]
    },
    entry_points={
        'console_scripts': [
            'authz_admin_service = oauth2.authz_admin_service.main:main',
            'authn_service = oauth2.authn_service.main:main',
            'authz_service = oauth2.authz_service.main:start',
            'client_admin_service = oauth2.client_admin_service.server:start',
            'dummy_authz_service = oauth2.dummy_authz_service.main:main',
        ],
    },
    setup_requires=[
        'setuptools_git',
    ],
)
