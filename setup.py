#!/usr/bin/env python
"""See <https://setuptools.readthedocs.io/en/latest/>.
"""
from setuptools import setup, find_packages


setup(
    # Publication Metadata:
    version='0.1.5',
    name='datapunt_authz_admin',
    description="User Role Management Service",
    # long_description="",
    url='https://github.com/Amsterdam/authz_admin',
    author='Amsterdam Datapunt',
    author_email='datapunt@amsterdam.nl',
    license='Mozilla Public License Version 2.0',
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],


    # Entry points:
    entry_points={
        'console_scripts': [
            'authz_admin = authz_admin.main:main'
        ],
    },


    # Packages and Package Data:
    package_dir={'': 'src'},
    packages=find_packages('src'),
    package_data={
        'authz_admin': ['config_schema*.json', 'openapi*.json', 'openapi.yml']
    },


    # Requirements:
    # setup_requires=[
    #     'setuptools_git',
    #     # Nice if you like setuptools integration for PyTest:
    #     #'pytest-runner',
    # ],
    install_requires=[
        # 'aiodns==1.1.1',
        # 'aiohttp==2.2.5',
        # 'aiohttp-debugtoolbar==0.4.1',
        # 'aiohttp-jinja2==0.14.0',
        # 'aiopg==0.13.1',
        # 'alabaster==0.7.10',
        # 'appnope==0.1.0',
        # 'argh==0.26.2',
        # 'asn1crypto==0.23.0',
        # 'async-timeout==1.4.0',
        # 'Babel==2.5.1',
        # 'bleach==2.1',
        # 'cchardet==2.1.1',
        # 'certifi==2017.7.27.1',
        # 'cffi==1.11.2',
        # 'chardet==3.0.4',
        # 'click==6.7',
        # 'coverage==4.4.1',
        # 'cryptography==2.3',
        # 'datapunt-authorization-django==0.2.23',
        # 'datapunt-config-loader==1.0.0',
        # 'decorator==4.1.2',
        # 'Django==1.11.7',
        # 'docutils==0.14',
        # 'entrypoints==0.2.3',
        # 'html5lib==1.0b10',
        # 'idna==2.6',
        # 'imagesize==0.7.1',
        # 'isort==4.2.15',
        # 'jedi==0.11.0',
        # 'Jinja2==2.9.6',
        # 'jsonschema==2.6.0',
        # 'livereload==2.5.1',
        # 'Mako==1.0.7',
        # 'MarkupSafe==1.0',
        # 'mimeparse==0.1.3',
        # 'mistune==0.7.4',
        # 'multidict==3.2.0',
        # 'pandocfilters==1.4.2',
        # 'parso==0.1.0',
        # 'pathtools==0.1.2',
        # 'pexpect==4.2.1',
        # 'pickleshare==0.7.4',
        # 'port-for==0.3.1',
        # 'prompt-toolkit==1.0.15',
        # 'psycopg2==2.7.3.1',
        # 'psycopg2-binary==2.7.5',
        # 'ptyprocess==0.5.2',
        # 'py==1.4.34',
        # 'pycares==2.3.0',
        # 'pycparser==2.18',
        # 'Pygments==2.2.0',
        # 'PyJWT==1.5.3',
        # 'python-dateutil==2.6.1',
        # 'python-editor==1.0.3',
        # 'pytz==2017.2',
        # 'PyYAML==3.12',
        # 'pyzmq==16.0.2',
        # 'qtconsole==4.3.1',
        # 'requests==2.18.4',
        # 'simplegeneric==0.8.1',
        # 'six==1.11.0',
        # 'snowballstemmer==1.2.1',
        # 'SQLAlchemy==1.1.0',
        # 'swagger-parser==1.0.0',
        # 'swagger-spec-validator==2.1.0',
        # 'terminado==0.6',
        # 'testpath==0.3.1',
        # 'tornado==4.5.2',
        # 'traitlets==4.3.2',
        # 'urllib3==1.22',
        # 'uvloop==0.8.1',
        # 'watchdog==0.8.3',
        # 'wcwidth==0.1.7',
        # 'webencodings==0.5.1',
        # 'yarl==0.12.0',

        'aiodns',  # Recommended by aiohttp docs
        'aiohttp==2.2.5',
        'aiohttp-jinja2==0.14.0',
        'aiopg',
        'datapunt-authorization-django==0.2.18',  # Only for jwks module in this package
        'cchardet',  # Recommended by aiohttp docs
        'datapunt-config-loader==1.0.0',
        'docutils',
        'jsonschema',
        'mimeparse',
        'PyYaml',
        'PyJWT',
        'psycopg2-binary',
        'SQLAlchemy==1.1',
        'swagger-parser',
        'uvloop==0.14.0',  # Recommended by aiohttp docs
        'yarl==0.12.0'
    ],
    extras_require={
        'docs': [
            'MacFSEvents==0.7',
            'Sphinx==1.6.4',
            'sphinx-autobuild==0.7.1',
            'sphinx-autodoc-typehints==1.2.3',
            'sphinx_rtd_theme==0.2.4',
        ],
        'test': [
            'alembic==0.9.5',
            'pytest==3.2.2',
            'pytest-cov==2.5.1',
            'pytest-aiohttp==0.1.3'
        ],
        'dev': [
            'aiohttp-devtools==0.5',
            'alembic==0.9.5',
            'jupyter==1.0.0',
        ]
    },
)
