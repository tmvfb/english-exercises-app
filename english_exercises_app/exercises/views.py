# from django.urls import reverse
from django.contrib import messages
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

# from english_exercises_app.mixins import MessagesMixin


@register.filter(name="split")
def split(value, key):
    return value.split(key)


class ExerciseUploadView(TemplateView):
    """
    This class defines logic of file upload.
    """

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
            print(form.errors)
            messages.warning(
                request, _("Something went wrong. Please check file format")
            )
            return redirect("exercise_upload")


class ExerciseCreateView(TemplateView):
    """
    This class defines the parameters that are sent to text_processing module.
    """

    def get(self, request):
        form = FilterForm()
        return render(request, "exercises/create.html", {"form": form})

    def post(self, request):
        form = FilterForm(request.POST)  # adds entry to Memory model

        if form.is_valid():
            # # TODO: more options to come
            # count = form.cleaned_data["count"]  # integer
            # pos = form.cleaned_data["pos"]  # list
            # ex_type = form.cleaned_data["exercise_type"]  # string
            # length = form.cleaned_data["length"]  # integer
            form.save(user=request.user)
            return redirect("exercise_show")

        else:
            messages.error(request, _("Please select valid parameters"))
            return redirect("exercise_create")


class ExerciseShowView(TemplateView):
    """
    This class shows exercises
    and adds user input to database to maintain stats.
    """

    def get(self, request):
        # check if any file was uploaded
        file = File.objects.filter(user=request.user).first()
        if file is not None:
            filepath = file.file.path
        else:
            messages.error(request, _("Please upload a file."))
            return redirect("exercise_upload")

        # retrieve current params for exercise generation
        params = Memory.objects.filter(user=request.user).first()

        # return user score if all exercises were completed
        if params.current_count == params.count:
            subquery = Exercise.objects.filter(user=request.user).order_by("-pk")[
                : params.count
            ]
            query = (
                Exercise.objects.filter(pk__in=subquery)
                .order_by("pk")
                .filter(flag=True)
            )
            score = query.count()

            messages.success(
                request,
                _(
                    f"You have completed all the exercises! Your score: {score} / {params.count}"   # noqa: E501
                ),
            )
            return redirect("exercise_create")

        elif request.GET.get("next") == "true":
            params.current_count += 1
            params.save()

        # refer to Memory model for details on kwargs
        kwargs = {
            field.name: getattr(params, field.name)  # fmt: skip
            for field in params._meta.fields
        }

        # prepare exercises and populate form fields
        data = prepare_exercises(filepath, **kwargs)
        e_type = data["exercise_type"]
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

        return render(
            request,
            "exercises/show.html",
            {
                "form": form,
                "count": params.count,
                "current_count": params.current_count,
            },
        )

    def post(self, request):
        form = TypeInExercise(request.POST)
        if request.POST.get("exercise_type") == "blanks":
            form = BlanksExercise(request.POST)
        print(request.POST.get("user_answer"))
        print(request.POST.get("correct_answer"))
        user = request.user

        # can get rid of this if pass the params with form
        params = Memory.objects.filter(user=user).first()

        if form.is_valid():
            correct_answer = form.cleaned_data["correct_answer"]
            user_answer = form.cleaned_data["user_answer"]
            print(correct_answer, user_answer)

            form.save(user=user)

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
                    "count": params.count,
                    "current_count": params.current_count,
                },
            )

        else:
            messages.error(request, _("Please provide a valid answer."))
            print(form.errors)
            return render(
                request,
                "exercises/show.html",
                {
                    "form": form,
                    "count": params.count,
                    "current_count": params.current_count,
                },
            )


class ExerciseStatsView(TemplateView):
    """
    Show exercise stats for the current user.
    """

    def get(self, request):
        user_stats = Exercise.objects.filter(user=request.user).order_by("-pk")

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
