from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
]
