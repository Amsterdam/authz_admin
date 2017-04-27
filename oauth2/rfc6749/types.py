"""
    oauth2.rfc6749.types
    ~~~~~~~~~~~~~~~~~~~~
"""
import collections


class ScopeTokenSet(frozenset):
    """ A frozenset that parses a space delimited string into an immutable
    sequence of scope-tokens.

    Per RFC 6749, section 3.3:

        The value of the scope parameter is expressed as a list of space-
        delimited, case-sensitive strings.  The strings are defined by the
        authorization server.  If the value contains multiple space-delimited
        strings, their order does not matter, and each string adds an
        additional access range to the requested scope.

            scope       = scope-token *( SP scope-token )
            scope-token = 1*( %x21 / %x23-5B / %x5D-7E )
    """

    allowed_charset = frozenset(
        chr(c) for c in (0x21, *range(0x23, 0x5B+1), *range(0x5D, 0x7D+1))
    )

    def __new__(cls, scope):
        if not isinstance(scope, str):
            raise ValueError(
                "ScopeTokenSet can only be created from a space delimited str"
            )
        scope_tokens = scope.split()
        if not all(set(s) <= cls.allowed_charset for s in scope_tokens):
            raise ValueError('scope-token can only contain {}'.format(
                set(cls.allowed_charset)
            ))
        return super().__new__(ScopeTokenSet, scope_tokens)


class Client(collections.namedtuple(
    'ClientRegistrationInfo', 'identifier name secret redirect_uris owner_id'
)):
    """ The registration information for a client.

    Per RFC 6749:

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
