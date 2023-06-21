from django import forms
from .models import File
from django.utils.translation import gettext_lazy as _


class FileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={
        "class": "form-control",
        "type": "file",
    }))

    class Meta:
        model = File
        fields = ["file"]

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')

        if file:
            filename = file.name
            print(filename)
            if not filename.endswith(('.txt', '.csv')):
                raise forms.ValidationError(_("Please check file format"))

        return file
