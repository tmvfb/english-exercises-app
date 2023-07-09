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
            ("DET", "Articles"),
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
            ("type_in", "Type in"),
            ("multiple_choice", "Multiple choice"),
            ("word_order", "Complete sentence"),
            ("blanks", "Complete blanks"),
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
        label=_("Context length"),
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    skip_length = forms.IntegerField(
        max_value=5,
        min_value=3,
        initial=3,
        label=_("Skipped words (complete sentence exercises only)"),
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Memory
        fields = ["count", "pos", "exercise_type", "length", "skip_length"]

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


class TypeInExercise(forms.ModelForm):
    """
    Base form for all types of exercises.
    """

    begin = forms.CharField(
        max_length=4095,
        widget=forms.HiddenInput(),
    )
    end = forms.CharField(
        max_length=2047,
        widget=forms.HiddenInput(),
        required=False
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
    """
    Used for both multiple choice and word order exercises.
    """

    user_answer = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )


class BlanksExercise(TypeInExercise):
    """
    Used for both multiple choice and word order exercises.
    """

    user_answer = forms.CharField(
        widget=forms.HiddenInput(),
        # widget=forms.RadioSelect(
        #     attrs={
        #         "class": "form-check-label",
        #         "type": "radio",
        #     }
        # ),
    )
    answers = forms.CharField(
        widget=forms.HiddenInput(),
    )
