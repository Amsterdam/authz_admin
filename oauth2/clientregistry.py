"""
    oauth2.clientregistry
    ~~~~~~~~~~~~~~~~~~~~~

    Convenient placeholder during developement. Will be replaced by an actual
    (database?) backend down the road.

    A registry entry contains, per RFC 6749:

    - identifier: unique string. RFC 6819 (OAuth2 threat model) doesn't mention
      that it must or should be random, so using a uuid version 4 suffices, I
      think. URL safety would be nice. For example:

      >> import base64
      >> import uuid
      >> base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]
      out[1]: b'NOadtMwDSQKmw30l4l2xxQ'

    - name: the application name
    - secret: -- only used by trusted clients -- random string with at least
      128 bits of entropy. For base 64 encoded secrets that means 6 bits per
      byte / character, so ~22 characters. We should use the secrets module for
      generating these. For example:

      >> import base64
      >> import secrets
      >> base64.standard_b64encode(secrets.token_bytes(16))[:-2]
      out[1]: b'XCAuw8B5u+EEBLALGOS9Aw'

    - redirect_uris: one or more (scheme, host, path, query) tuples.


    At Datapunt we'd like a little more information, independent of the RFC:

    - user id of client owner. Note that this implies the owner must be a
      person. What this looks like depends on our user registration. For now,
      remains undecided.
"""
import collections


RedirectURI = collections.namedtuple(
    'RedirectURI', 'scheme host path query'
)

RegistryEntry = collections.namedtuple(
    'Client', 'identifier name secret redirect_uris owner_id'
)

# A registry to loop over (O(N) lookups)
_registry = (
    RegistryEntry(
        identifier=b'NOadtMwDSQKmw30l4l2xxQ.data.amsterdam',
        name='Atlas',
        secret=None,  # Atlas is an untrusted client
        owner_id='datapunt',
        redirect_uris=(
            RedirectURI(scheme='http', host='localhost', path='', query=''),
        ),
    ),
)


def get(identifier, secret=None):
    """ Get client information from the client registry based on a client
    identifier.
    """
    if secret is not None and len(secret) != 22:
        raise Exception('Not a valid secret: {}'.format(secret))
    result = tuple(e for e in _registry if e.identifier == identifier)
    return (result and result[0]) or None
