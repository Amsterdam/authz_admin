from . import views


def setup_routes(app):
    app.router.add_get('/authorize', views.authorizationrequest)
    app.router.add_get('/idps/{idp}/token', views.idp_token)
    app.router.add_get('/idps/{idp}/code', views.idp_code)
