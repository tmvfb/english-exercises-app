from django import forms
from django.utils.translation import gettext_lazy as _

from text_processing.prepare_data import remove_data

from .models import Exercise, File, Memory


class FileForm(forms.ModelForm):
    """
    Form for file upload. Has file format check.
    1 entry per user.
    """

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
        """
        Checks file format.
        """

        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        if file and not file._name.endswith((".txt", ".csv")):
            raise forms.ValidationError(_("Incorrect file format"))

        return cleaned_data

    def save(self, user, commit=True):
        # delete previous files and db entry, if exist
        file = File.objects.filter(user=user).first()
        if file is not None:
            remove_data(file.file.path, str(user))  # rm associated json
            file.file.delete()
            file.delete()

        instance = super().save(commit=False)
        instance.user = user
        if commit:
            instance.save()
        return instance


class FilterForm(forms.ModelForm):
    """
    Sets current parameters for exercise generation and stores them in
    Memory model. 1 entry per user.
    """

    count = forms.IntegerField(
        initial=50,
        widget=forms.NumberInput(
            attrs={
                "class": "form-range",
                "type": "range",
                "min": 1,
                "max": 99,
                "step": 1,
                "id": "rangeInput",
            }
        ),
    )
    pos = forms.MultipleChoiceField(
        label=_("Parts of speech"),
        choices=(
            ("ALL", "All"),
            ("VERB", "Verbs"),
            ("NOUN", "Nouns"),
            ("ADJ", "Adjectives"),
        ),
        initial="ALL",
        widget=forms.CheckboxSelectMultiple(
            attrs={
                # "class": "form-select",
                "multiple": True,
            }
        ),
    )
    exercise_type = forms.ChoiceField(
        label=_("Exercise type"),
        choices=(
            ("all_choices", "All"),
            ("multiple_choice", "Multiple choice"),
            ("type_in", "Type in"),
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
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Memory
        fields = ["count", "pos", "exercise_type", "length"]

    def save(self, user, commit=True):
        # delete previous entry, if exists
        memory = Memory.objects.filter(user=user).first()
        if memory is not None:
            memory.delete()

        instance = super().save(commit=False)
        instance.user = user
        if commit:
            instance.save()
        return instance


# let's have one form per every exercise
class TypeInExercise(forms.ModelForm):
    begin = forms.CharField(
        max_length=1023,
        widget=forms.HiddenInput(),
    )
    end = forms.CharField(
        max_length=1023,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Exercise
        fields = ["user_answer", "exercise_type", "correct_answer"]
        widgets = {
            "user_answer": forms.TextInput(attrs={"class": "form-control"}),
            "exercise_type": forms.HiddenInput(),
            "correct_answer": forms.HiddenInput(),
        }

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user
        if commit:
            instance.save()
        return instance


class MultipleChoiceExercise(TypeInExercise):
    user_answer = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
