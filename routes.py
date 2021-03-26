import views


def setup_routes(app):
    router = app.router
    router.add_get('/test', views.handle)
    router.add_get('/users', views.UsersView.get_all_users)
    router.add_post('/registration', views.UsersView.register_new_user)
    router.add_post('/login', views.UsersView.authorization)
    router.add_route('GET', '/exc', views.exception_handler,
                     name='exc_example')
