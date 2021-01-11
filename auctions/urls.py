from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:pk>", views.read_listing, name="read_listing"),
    path("close_listing", views.close_listing, name="close_listing"),
    path("create_bid", views.create_bid, name="create_bid"),
]
