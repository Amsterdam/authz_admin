import time

import pytest
import jwt

from authz_admin.config import load as load_config


@pytest.fixture(scope='session')
def aaconfig():
    # language=rst
    """Fixture that gives access to a loaded configuration file."""
    return load_config()


@pytest.fixture(scope='session')
def access_token(aaconfig):
    # language=rst
    """Fixture that gives a valid access token to use."""
    now = int(time.time())
    token_dict = {
        'iat': now,
        'exp': now + 3600 * 12,
        'scopes': ['AUR/R', 'AUR/W'],
    }
    return jwt.encode(
        token_dict,
        key=aaconfig['authz_admin']['access_secret'],
        algorithm='HS256'
    )
