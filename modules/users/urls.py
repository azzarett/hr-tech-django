from django.urls import path
from modules.users.controllers.users_controller import UsersController

users = UsersController.as_view

urlpatterns = [
    path("", users({"get": "list"})),
    path("/token", users({"post": "token"})),
    path("/me", users({"get": "me"})),
    path("/me/update", users({"patch": "update_me"})),
    path("/<uuid:pk>", users({"get": "retrieve", "delete": "destroy"})),
]
