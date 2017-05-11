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


def idp_callback_uri(request, for_idp):
    """
    """
    path = request.app.router[_IDP_CALLBACK].url_for(idp=for_idp)
    current_url = request.url
    port = (current_url.port not in {None, 80, 443} and ':%d' % current_url.port) or ''
    return '{}://{}{}{}'.format(current_url.scheme, current_url.host, port, path)
