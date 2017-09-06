import pytest

from authz_admin.config import load as load_config


@pytest.fixture(scope='module')
def aaconfig():
    """Fixture that gives access to a loaded configuration file."""
    return load_config()
