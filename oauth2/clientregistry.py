"""
    oauth2.clientregistry
    ~~~~~~~~~~~~~~~~~~~~~

    Convenient placeholder during developement. Will be replaced by an actual
    (database?) backend down the road.
"""
from .rfc6749 import Client

# A registry to loop over (O(N) lookups)
_registry = (
    Client(
        identifier=b'NOadtMwDSQKmw30l4l2xxQ.data.amsterdam',
        name='Atlas',
        secret=None,  # Atlas is an untrusted client
        owner_id='datapunt',
        redirect_uris=(
            'http://localhost',
        ),
    ),
)


def get(identifier):
    """ Get client information from the client registry based on a client
    identifier.
    """
    result = tuple(e for e in _registry if e.identifier == identifier)
    return (result and result[0]) or None
