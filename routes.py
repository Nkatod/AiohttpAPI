import views


def setup_routes(app):
    router = app.router
    router.add_get('/test', views.handle)
    router.add_post('/registration', views.register_new_user)
    router.add_route('GET', '/exc', views.exception_handler,
                     name='exc_example')
