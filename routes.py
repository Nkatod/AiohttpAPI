import views


def setup_routes(app):
    router = app.router
    router.add_get('/', views.handle)
    router.add_get('/users', views.UsersView.get_all_users)
    router.add_post('/registration', views.UsersView.register_new_user)
    router.add_post('/login', views.UsersView.authorization)
    router.add_post('/items/new', views.ItemsView.create_new_item)
    router.add_delete('/items/{item_id}', views.ItemsView.delete_item)
    router.add_get('/items', views.ItemsView.get_user_items)
    router.add_post('/send', views.ItemsView.send_item)
    router.add_get('/get', views.ItemsView.move_item)
    router.add_route('GET', '/exc', views.exception_handler,
                     name='exc_example')
