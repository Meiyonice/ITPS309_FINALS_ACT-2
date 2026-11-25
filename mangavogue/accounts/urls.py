from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    AppLoginView,
    forgot_password_view,
    home,
    password_reset_complete_view,
    register_view,
    set_new_password_view,
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", AppLoginView.as_view(), name="login"),
    path("register/", register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", forgot_password_view, name="password_reset"),
    path(
        "password-reset/new/",
        set_new_password_view,
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        password_reset_complete_view,
        name="password_reset_complete",
    ),
]
