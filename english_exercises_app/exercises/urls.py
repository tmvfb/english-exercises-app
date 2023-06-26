from django.urls import path

from . import views

urlpatterns = [
    path('', views.ExerciseShowView.as_view(), name='exercise_show'),  # noqa: E501
    path('upload/', views.ExerciseUploadView.as_view(), name='exercise_upload'),  # noqa: E501
    path('create/', views.ExerciseCreateView.as_view(), name='exercise_create'),  # noqa: E501
    path('stats/', views.ExerciseStatsView.as_view(), name='exercise_stats'),  # noqa: E501
]
