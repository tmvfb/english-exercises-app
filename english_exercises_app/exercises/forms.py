from django import forms
from .models import File, Exercise
from django.utils.translation import gettext_lazy as _


class FileForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "type": "file",
            }
        )
    )

    class Meta:
        model = File
        fields = ["file"]

    def clean(self):
        '''
        Checks file format.
        '''

        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file:
            filename = file.name
            print(filename)
            if not filename.endswith((".txt", ".csv")):
                raise forms.ValidationError(_("Incorrect file format"))

        return file


class FilterForm(forms.Form):
    count = forms.IntegerField(
        initial=50,
        widget=forms.NumberInput(
            attrs={
                "class": "form-range",
                "type": "range",
                "min": 1,
                "max": 99,
                "step": 1,
                "id": "rangeInput"
            }
        ),
    )
    pos = forms.MultipleChoiceField(
        label=_("Parts of speech"),
        choices=(("v", "Verbs"), ("n", "Nouns"), ("a", "Adjectives")),
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "multiple": True
            }
        ),
    )
    type_ = forms.ChoiceField(
        label=_("Exercise type"),
        choices=(
            ("a", "All"),
            ("m", "Multiple choice"),
            ("t", "Type in"),
        ),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    length = forms.IntegerField(
        max_value=10,
        min_value=1,
        initial=1,
        label=_("Sentences per exercise"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control"
            }
        )
    )


# let's have one form per every exercise
class TypeInExercise(forms.Form):
    class Meta:
        model = Exercise
        fields = ['user', 'user_answer', 'correct_answer', 'exercise_type']
        widgets = {
            "user_answer": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "user": forms.HiddenInput(),
            "correct_answer": forms.HiddenInput(),
            "exercise_type": forms.HiddenInput()
        }
