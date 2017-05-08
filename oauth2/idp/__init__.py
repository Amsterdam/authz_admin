"""
    oauth2.idp
    ~~~~~~~~~~

    Package containing IdP plugins. An IdP plugin must support the following
    contract:

    ::

        IDP_ID = ...  # a urlsafe identifier for this idp

        def get(config):
            \""" Return the IdP plugin interface bound to the given
            configuration.
            \"""
            return (
                authentication_redirect,
                validate_authentication
            )

    Where the return values have the following signatures:

    ::

        def authentication_redirect(uuid):
            \""" Redirect to the login page of the IdP

            :param uuid:
                An opaque identifier
            :return Response, [key, [value=uuid]]:
                An aiohttp HTTP Response object, an optional key and an optional
                value. If given, the ``key`` and ``value`` will be stored for
                retrieval in ``validate_authentication``
            \"""


        def validate_authentication(request, get_and_delete):
            \""" Validate that a user has authenticated

            :param request:
                An aiohttp Request object
            :param get_and_delete:
                A callable that takes a key and returns the corresponding value.
                This is a service that provides sharing state between a call to
                ``authentication_redirect`` and ``validate_authentication``.
            :raises oauth2.idp.FailedAuthentication:
                If for whatever reason authentication has failed.
            :return uuid, user_id, [user_props]:
                The uuid corresponding to the call to
                ``authentication_redirect``, the authenticated user's
                identifier, and the authenticated user's properties, if any.
            \"""
"""
