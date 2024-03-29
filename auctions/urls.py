from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('create_listing', views.create_listing, name='create_listing'),
    path('listing/<int:pk>', views.read_listing, name='read_listing'),
    path('watchlist', views.read_watchlist, name='read_watchlist'),
    path('categories', views.read_categories, name='read_categories'),
    path('category/<int:pk>', views.read_category, name='read_category'),
]
