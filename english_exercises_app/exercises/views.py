from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import QueryDict
from django.shortcuts import redirect, render
from django.template.defaulttags import register
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView

from text_processing.prepare_data import prepare_exercises

from .forms import (
    BlanksExercise,
    FileForm,
    FilterForm,
    MultipleChoiceExercise,
    TypeInExercise,
)
from .models import Exercise, File, Memory


@register.filter(name="split")
def split(value, key):
    return value.split(key)


class ExerciseUploadView(LoginRequiredMixin, TemplateView):
    """
    This class defines logic of file upload.
    """

    login_url = "/users/login/"

    def get(self, request):
        form = FileForm()
        return render(request, "exercises/upload.html", {"form": form})

    def post(self, request):
        form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, _("File uploaded successfully!"))
            return redirect("exercise_create")

        else:
            messages.warning(
                request, _("Something went wrong. Please check file format")
            )
            return redirect("exercise_upload")


class ExerciseCreateView(LoginRequiredMixin, TemplateView):
    """
    This class defines the parameters that are sent to text_processing module.
    """

    login_url = "/users/login/"

    def get(self, request):
        form = FilterForm()
        return render(request, "exercises/create.html", {"form": form})

    def post(self, request):
        form = FilterForm(request.POST)  # adds entry to Memory model

        if form.is_valid():
            form.save(user=request.user)
            return redirect("exercise_show")

        else:
            messages.error(request, _("Please select valid parameters"))
            return redirect("exercise_create")


class ExerciseShowView(LoginRequiredMixin, TemplateView):
    """
    This class shows exercises
    and adds user input to database to maintain stats.
    """

    login_url = "/users/login/"

    def calculate_user_score(self, request, params):
        subquery = Exercise.objects.filter(user=request.user).order_by("-pk")[
            : params.count
        ]
        query = (
            Exercise.objects.filter(pk__in=subquery).order_by("pk").filter(flag=True)
        )
        score = query.count()

        messages.success(
            request,
            _(
                f"You have completed all the exercises! Your score: {score} / {params.count}"  # noqa: E501
            ),
        )
        return redirect("exercise_create")

    def populate_exercise_form(self, data: QueryDict or dict) -> dict:
        """
        Function populates form data for all exercise types.
        """

        if isinstance(data, QueryDict):  # handling post request
            form = TypeInExercise(data)
            if data.get("exercise_type") == "blanks":
                form = BlanksExercise(data)
            return form

        # handling get request
        e_type = data["exercise_type"]
        hints = {
            "type_in": _("Type your answer"),
            "multiple_choice": _("Select correct answer"),
            "word_order": _("Select correct answer"),
            "blanks": _("Drag and drop correct answers"),
        }
        initial_data = {
            "exercise_type": e_type,
            "correct_answer": data["correct_answer"],
            "begin": data["begin"],
            "end": data["end"],
        }
        if e_type == "type_in":
            form = TypeInExercise(initial=initial_data)
        elif e_type in ["multiple_choice", "word_order"]:
            form = MultipleChoiceExercise(initial=initial_data)
            form.fields["user_answer"].choices = data["options"]
        elif e_type == "blanks":
            form = BlanksExercise(initial=initial_data)
            form.fields["answers"].initial = data["options"]
        form.fields["hint"].initial = hints[e_type]
        form.fields["count"].initial = data["count"]
        form.fields["current_count"].initial = data["current_count"]
        return form

    def get(self, request):
        file = File.objects.filter(user=request.user).first()
        params = Memory.objects.filter(user=request.user).first()

        if not file:
            messages.error(request, _("Please upload a file."))
            return redirect("exercise_upload")
        if not params:
            messages.error(request, _("Please specify exercise parameters."))
            return redirect("exercise_create")

        if params.current_count == params.count:
            return self.calculate_user_score(request, params)

        if request.GET.get("next") == "true":
            params.current_count += 1
            params.save()

        # prepare exercises
        try:
            # refer to Memory model for details on kwargs
            kwargs = {
                field.name: getattr(params, field.name)  # fmt: skip
                for field in params._meta.fields
            }
            filepath = file.file.path
            data = prepare_exercises(filepath, **kwargs)
        except FileNotFoundError:
            messages.warning(request, _("Please upload a file"))
            return redirect("exercise_upload")

        # populate form fields
        data["count"] = params.count
        data["current_count"] = params.current_count
        form = self.populate_exercise_form(data)

        return render(request, "exercises/show.html", {"form": form})

    def post(self, request):
        form = self.populate_exercise_form(request.POST)

        if form.is_valid():
            correct_answer = form.cleaned_data["correct_answer"]
            user_answer = form.cleaned_data["user_answer"]

            form.save(user=request.user)

            if user_answer == correct_answer:
                hide_correct = True
                messages.success(request, _("Correct!"))
                if form.cleaned_data["exercise_type"] == "blanks":
                    hide_correct = False
            else:
                hide_correct = False
                messages.error(request, _("Sorry, your answer is incorrect"))

            return render(
                request,
                "exercises/show.html",
                {
                    "form": form,
                    "button_status": "disabled",
                    "correct_answer": None if hide_correct else correct_answer,
                },
            )

        else:
            messages.error(request, _("Please provide a valid answer."))
            return render(request, "exercises/show.html", {"form": form})


class ExerciseStatsView(LoginRequiredMixin, TemplateView):
    """
    Show exercise stats for the current user.
    """

    login_url = "/users/login/"

    def get(self, request):
        user_stats = Exercise.objects.filter(user=request.user).order_by("-pk")

        if user_stats.count() == 0:
            messages.warning(
                request,
                _("No exercises have been completed yet, stats are not available."),
            )
            return redirect("home")

        subquery = user_stats[:100]
        query_total = Exercise.objects.filter(pk__in=subquery).count()
        query_correct = (
            Exercise.objects.filter(pk__in=subquery).filter(flag=True).count()
        )

        total_count = user_stats.count()
        correct_count = user_stats.filter(flag=True).count()
        percentage_last_100 = f"{query_correct / query_total:.1%}"

        return render(
            request,
            "exercises/stats.html",
            {
                "total_count": total_count,
                "correct_answers": correct_count,
                "percentage": percentage_last_100,
            },
        )
