from django.db import models
from django.conf import settings


class File(models.Model):
    """
    Restrict user to have only one file uploaded.
    """

    file = models.FileField(
        upload_to="",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )


class Exercise(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    exercise_type = models.CharField(max_length=255)
    user_answer = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    flag = models.BooleanField()

    def save(self, *args, **kwargs):
        if self.user_answer == self.correct_answer:
            self.flag = True
        else:
            self.flag = False
        super().save(*args, **kwargs)
