"""
Module that loads the configuration settings for all our services.

See also :mod:`config_loader`.

**Example usage**::

    from oauth2 import config
    CONFIG = config.get()
    os.chdir(CONFIG['working_directory'])

..  py:data:: CONFIG_SCHEMA_V1_PATH

    :vartype: `pathlib.Path`

..  py:data:: DEFAULT_CONFIG_PATHS

    :vartype: list[`pathlib.Path`]

    By default, this variable is initialized with:

        -   :file:`/etc/datapunt-oauth2.yml`
        -   :file:`./datapunt-oauth2.yml`
            relative to the current working directory


"""

import functools
import pathlib
import os
import config_loader

from .frozen import frozen

DEFAULT_CONFIG_PATHS = [
    pathlib.Path('/etc') / 'datapunt-oauth2.yml',
    pathlib.Path('datapunt-oauth2.yml')
]


CONFIG_SCHEMA_V1_PATH = pathlib.Path(
    os.path.dirname(os.path.abspath(__file__))
) / 'config_schema_v1.json'


@functools.lru_cache()
def get():
    """
    Load, parse and validate the configuration file from
    one of the `DEFAULT_CONFIG_PATHS` or from the location
    given in the :envvar:`CONFIG_PATH` environment variable.

    :rtype: dict
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
        raise config_loader.ConfigError(error_msg.format(paths_as_string))
    return frozen(config_loader.load(
        filtered_config_paths[0],
        CONFIG_SCHEMA_V1_PATH
    ))
