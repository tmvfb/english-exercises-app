from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.UserCreateView.as_view(), name='user_create'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout')
]
