from django.urls import path

from . import views

urlpatterns = [
    path("create/", views.UserCreateView.as_view(), name="user_create"),
    path("update/", views.UserPasswordUpdateView.as_view(), name="user_update"),
    path("delete/<int:pk>/", views.UserDeleteView.as_view(), name="user_delete"),
    path("settings/", views.UserSettingsView.as_view(), name="user_settings"),
    path("login/", views.UserLoginView.as_view(), name="user_login"),
    path("logout/", views.UserLogoutView.as_view(), name="user_logout"),
]
