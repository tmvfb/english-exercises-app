from django import forms
from django.utils.translation import gettext_lazy as _


class FileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={
        "class": "form-control",
        "type": "file",
    }))
