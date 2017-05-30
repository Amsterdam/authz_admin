"""
Module that loads configuration settings from a yaml file.

**Features**

- Environment interpolation with defaults
- JSON schema validation

**Example usage**::

    import config_loader
    CONFIG = config_loader.load(
        path_to_config_file,
        path_to_config_schema_file
    )

"""

from .config_loader import *
