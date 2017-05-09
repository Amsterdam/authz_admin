from . import views


def setup_routes(app, root):
    if len(root) and root[0] != '/':
        root = '/' + root
    if len(root) and root[-1] == '/':
        root = root[:-1]
    app.router.add_get(root + '/authorize', views.authorizationrequest)
    app.router.add_get(root + '/idps/{idp}/token', views.idp_token)
    app.router.add_get(root + '/idps/{idp}/code', views.idp_code)
