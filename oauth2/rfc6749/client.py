"""
    oauth2.rfc6749
    ~~~~~~~~~~~~~~

    The registration information for a client, per RFC 6749:

    - identifier (Section 2.2): unique string.Using a uuid version 4 suffices,
      I think. URL safety would be nice. For example:

      >> import base64
      >> import uuid
      >> base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]
      out[1]: b'NOadtMwDSQKmw30l4l2xxQ'

    - secret / password (Section 2.3.1): -- only used by trusted clients --
      random string with at least 128 bits of entropy. For base 64 encoded
      secrets that means 6 bits per byte / character, so ~22 characters. We
      should use the secrets module for generating these. For example:

      >> import base64
      >> import secrets
      >> base64.standard_b64encode(secrets.token_bytes(16))[:-2]
      out[1]: b'XCAuw8B5u+EEBLALGOS9Aw'

    - redirect_uris (Section 3.1.2): The redirection endpoint URI MUST be an
      absolute URI as defined by [RFC3986] Section 4.3.  The endpoint URI MAY
      include an "application/x-www-form-urlencoded" formatted (per Appendix B)
      query component ([RFC3986] Section 3.4), which MUST be retained when
      adding additional query parameters.  The endpoint URI MUST NOT include a
      fragment component.


    In addition to RFC 6749, our implementation requires:

    - name: the application name
    - user id of client owner. Note that this implies the owner must be a
      person. What this looks like depends on our user registration. For now,
      remains undecided.
"""
import collections


ClientRegistrationInfo = collections.namedtuple(
    'ClientRegistrationInfo', 'identifier name secret redirect_uris owner_id'
)


class Client(ClientRegistrationInfo):
    ...
