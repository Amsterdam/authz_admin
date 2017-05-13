"""
Module that loads the configuration settings for all our services.

See also :mod:`.config_loader`.

.. _default-config-locations:

**Default config file locations**

- ``/etc/datapunt-oauth2.yml``
- ``$PROJECT/config.yml``, where ``$PROJECT`` is the parent directory of
   :mod:`oauth2`, which is useful during development.

**Example usage**::

    from oauth2 import config
    CONFIG = config.get()
"""

import functools
import os
import pathlib

from . import config_loader


_PROJECT_PATH = pathlib.Path(
    os.path.dirname(os.path.abspath(__file__))
).parent.parent
"""
:vartype: `pathlib.Path`
"""


DEFAULT_CONFIG_PATHS = [
    pathlib.Path('/etc') / 'datapunt-oauth2.yml',
    _PROJECT_PATH / 'config.yml',
]
"""
:vartype: list(`pathlib.Path`)
"""


_CONFIG_SCHEMA_V1_PATH = _PROJECT_PATH / 'config_schema_v1.json'
"""
:vartype: `pathlib.Path`
"""


@functools.lru_cache()
def get():
    """
    Load, parse and validate the configuration file from one of the
    :ref:`default locations <default-config-locations>` or from the location
    given in the ``CONFIG_PATH`` environment variable.

    :returns: the “raw” config as read from file.
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
    return config_loader.load(
        filtered_config_paths[0],
        _CONFIG_SCHEMA_V1_PATH
    )
