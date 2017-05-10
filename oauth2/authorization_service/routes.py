""" Routes and reverse route lookups
"""
_IDP_CALLBACK = 'idp-callback'


def register_routes(app, root, requesthandler):
    """ Register all resources.
    """
    app.router.add_get(
        root + '/authorize', requesthandler.authorization)
    app.router.add_get(
        root + '/idps/{idp}', requesthandler.idp_callback, name=_IDP_CALLBACK)


def idp_callback_uri(app, for_idp):
    """
    """
    path = app.router[_IDP_CALLBACK].url_for(idp=for_idp)
