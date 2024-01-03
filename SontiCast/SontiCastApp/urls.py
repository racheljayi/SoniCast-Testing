from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("callback/", views.callback, name="callback"),
    path("results/", views.results, name="results"),
    path('playlist-made/', views.make_playlist, name="make_playlist"),
]