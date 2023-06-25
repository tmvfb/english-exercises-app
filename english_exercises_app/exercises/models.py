from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _


class File(models.Model):
    """
    Restricts user to have only one file uploaded.
    Stores information about the current file.
    """

    file = models.FileField(
        upload_to="",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")


class Exercise(models.Model):
    """
    Stores information about user answers.
    """

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

    def __str__(self):
        return (
            f'{self.exercise_type = }\n'
            f'{self.user_answer = }\n'
            f'{self.correct_answer = }\n'
            f'{self.flag = }'
        )

    class Meta:
        verbose_name = _("Exercise")
        verbose_name_plural = _("Exercises")


class Memory(models.Model):
    """
    Stores current parameters for exercises.
    Has method to increment number of current exercise.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    current_count = models.IntegerField(default=0)
    count = models.IntegerField()

    # this limits possible db options to postgres
    pos = ArrayField(base_field=models.CharField(max_length=63))

    exercise_type = models.CharField(max_length=255)
    length = models.IntegerField()

    @classmethod
    def get_current_count(cls):
        counter, created = cls.objects.get_or_create(pk=1)
        return counter.current_count

    @classmethod
    def increment_count(cls):
        counter, created = cls.objects.get_or_create(pk=1)
        counter.current_count += 1

        if counter.current_count == counter.count:
            counter.delete()
        else:
            counter.count += 1
            counter.save()
