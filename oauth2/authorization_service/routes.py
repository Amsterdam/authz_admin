from . import views


def setup_routes(app):
    app.router.add_get('/authorize', views.authorizationrequest)