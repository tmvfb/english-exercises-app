from django.urls import path

from . import views

urlpatterns = [
    path("", views.ExerciseShowView.as_view(), name="exercise_show"),
    path("upload/", views.ExerciseUploadView.as_view(), name="exercise_upload"),
    path("create/", views.ExerciseCreateView.as_view(), name="exercise_create"),
    path("stats/", views.ExerciseStatsView.as_view(), name="exercise_stats"),
    path(
        "stats/delete/",
        views.ExerciseStatsDeleteView.as_view(),
        name="exercise_stats_delete",
    ),
]
