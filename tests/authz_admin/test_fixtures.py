import pytest

from authz_admin.config import load as load_config


@pytest.fixture(scope='session')
def aaconfig():
    # language=rst
    """Fixture that gives access to a loaded configuration file."""
    return load_config()
