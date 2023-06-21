from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


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
