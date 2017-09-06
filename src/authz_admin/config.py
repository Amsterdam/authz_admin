"""
Module that loads the configuration settings for all our services.

.. envvar:: CONFIG_PATH

    If set, the configuration is loaded from this path.

See also :mod:`config_loader`.

**Example usage**::

    from authz_admin import config
    os.chdir(config.get()['working_directory'])


..  py:data:: CONFIG_SCHEMA_V1_PATH

    :vartype: `pathlib.Path`

..  py:data:: DEFAULT_CONFIG_PATHS

    :vartype: list[`pathlib.Path`]

    By default, this variable is initialized with:

        -   :file:`/etc/datapunt-oauth2.yml`
        -   :file:`./datapunt-oauth2.yml`

"""

import logging
import logging.config
import os.path
import pathlib
import re
import typing as T

import config_loader
from .frozen import frozen

_logger = logging.getLogger(__name__)


DEFAULT_CONFIG_PATHS = [
    pathlib.Path('/etc') / 'datapunt-oauth2.yml',
    pathlib.Path('datapunt-oauth2.yml'),
    pathlib.Path('../datapunt-oauth2.yml')
]


CONFIG_SCHEMA_V1_PATH = pathlib.Path(
    os.path.dirname(os.path.abspath(__file__))
) / 'config_schema_v1.json'


RE_DATASET_ID = re.compile(r'\w{1,4}')
RE_SCOPE_ID = re.compile(r'\w{1,4}')


def _config_path():
    # language=rst
    """
    Determines which path to use for the configuration file.

    :rtype: pathlib.Path
    :raises: FileNotFoundError

    """
    config_paths = [pathlib.Path(os.getenv('CONFIG_PATH'))] \
        if os.getenv('CONFIG_PATH') \
        else DEFAULT_CONFIG_PATHS

    filtered_config_paths = list(filter(
        lambda path: path.exists() and path.is_file(),
        config_paths
    ))

    if 0 == len(filtered_config_paths):
        error_msg = 'No configfile found at {}'
        paths_as_string = ' or '.join(str(p) for p in config_paths)
        raise FileNotFoundError(error_msg.format(paths_as_string))
    return filtered_config_paths[0]


def _validate_datasets_and_scope_ids(config):
    datasets = config['authz_admin']['datasets']
    for dataset_id, dataset in datasets.items():
        assert RE_DATASET_ID.fullmatch(dataset_id)
        dataset_name = dataset['name']
        assert len(dataset_name) > 0
        assert len(dataset_name) <= 80
        scopes = dataset['scopes']
        for scope_id, scope in scopes.items():
            assert RE_SCOPE_ID.fullmatch(scope_id)
            scope_name = scope['name']
            assert len(scope_name) > 0
            assert len(scope_name) <= 80


def _validate_scopes(config):
    # language=rst
    """
    Validate internal consistancy of scope relations ``includes`` and ``included_by``.

    :raises: config_loader.ConfigError

    """
    for ds_token, dataset in config['authz_admin']['datasets'].items():
        for scope_token, scope in dataset.get('scopes', dict()).items():
            includes = scope.get('includes')
            included_by = scope.get('included_by')
            try:
                if includes is not None:
                    assert dataset['scopes'][includes]['included_by'] == scope_token
                if included_by is not None:
                    assert dataset['scopes'][included_by]['includes'] == scope_token
            except Exception:
                error_message = "'includes' or 'included_by' relation of scope '{}.{}' isn't reciprocated."
                raise config_loader.ConfigError(error_message.format(ds_token, scope_token)) from None


def load():
    # language=rst
    """
    Load and validate the configuration.

    :rtype: types.MappingProxyType

    .. todo:: Log the chosen path with proper log level.

    """
    config_path = _config_path()
    config = config_loader.load(
        config_path,
        CONFIG_SCHEMA_V1_PATH
    )
    logging.config.dictConfig(config['logging'])
    _logger.info("Loaded configuration from '%s'", os.path.abspath(config_path))
    # Procedure logging.config.dictConfig() (called
    # above) requires a MutableMapping as its input,
    # so we only freeze config *after* that call:
    config = frozen(config)
    _validate_datasets_and_scope_ids(config)
    _validate_scopes(config)
    return config


def all_scopes(config: T.Hashable) -> T.FrozenSet[str]:
    # language=rst
    """All scopes defined in the configuration.

    To be precise, this function returns a frozen set of fully qualified scope
    identifiers:

    ..  code-block:: abnf

        fq_scope_id = dataset_id "." scope_id
        dataset_id = 1# token_char
        scope_id = 1# token_char
        token_char = ...

    """
    retval = []
    for dataset_token, dataset in config['authz_admin']['datasets'].items():
        for scope_token in dataset.get('scopes', {}):
            retval.append("{}.{}".format(dataset_token, scope_token))
    return frozenset(retval)
