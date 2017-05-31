"""
Module that loads the configuration settings for all our services.

.. envvar:: CONFIG_PATH

    If set, the configuration is loaded from this path.

See also :mod:`config_loader`.

**Example usage**::

    from oauth2 import config
    os.chdir(config.get()['working_directory'])


..  py:data:: CONFIG_SCHEMA_V1_PATH

    :vartype: `pathlib.Path`

..  py:data:: DEFAULT_CONFIG_PATHS

    :vartype: list[`pathlib.Path`]

    By default, this variable is initialized with:

        -   :file:`/etc/datapunt-oauth2.yml`
        -   :file:`./datapunt-oauth2.yml`

"""

import functools
import pathlib
import os
import config_loader
import logging.config

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


def _config_path():
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


def _validate_scopes(config):
    """
    Validate internal consistancy of scope relations ``includes`` and ``included_by``.

    :raises: config_loader.ConfigError

    """
    for ds_token, dataset in config.get('datasets', dict()).items():
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


@functools.lru_cache()
def get():
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
    _logger.info("Loaded configuration from '%s'", config_path)
    # Procedure logging.config.dictConfig() (called
    # above) requires a MutableMapping as its input,
    # so we only freeze config *after* that call:
    config = frozen(config)
    _validate_scopes(config)
    return config
