# from django.urls import reverse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.contrib import messages
from .forms import FileForm, FilterForm, TypeInExercise
from .models import File
from text_processing.prepare_data import prepare_exercises

# from english_exercises_app.mixins import MessagesMixin


class ExerciseUploadView(TemplateView):
    def get(self, request):
        form = FileForm()
        return render(request, "exercises/upload.html", {"form": form})

    def post(self, request):
        form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            # delete previous file and db entry, if exist
            try:
                previous_file = File.objects.get(user=request.user)
                previous_file.file.delete()
                previous_file.delete()
            except File.DoesNotExist:
                pass

            file_instance = File(file=request.FILES["file"], user=request.user)
            file_instance.save()
            messages.success(request, _("File uploaded successfully!"))
            return render(request, "exercises/upload.html", {"form": form})

        else:
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
        form = FilterForm(request.POST)

        if form.is_valid():
            # TODO: more options to come
            count = form.cleaned_data["count"]  # integer
            pos = form.cleaned_data["pos"]  # list
            ex_type = form.cleaned_data["type_"]  # string
            length = form.cleaned_data["length"]  # integer

            exercises = prepare_exercises(count, pos, ex_type, length)

            return HttpResponse(exercises)

        else:
            return redirect("exercise_show")


class ExerciseShowView(TemplateView):
    """
    This class shows exercises
    and adds user input to database to maintain stats.
    """

    def get(self, request):
        data = prepare_exercises()
        form = TypeInExercise(
            initial={
                "exercise_type": data["exercise_type"],
                "correct_answer": data["correct_answer"],
            }
        )
        return render(
            request,
            "exercises/show.html",
            {
                "form": form,
                "begin": data["sentence"][0],
                "end": data["sentence"][1],
            },
        )

    def post(self, request):
        form = TypeInExercise(request.POST)

        if form.is_valid():
            user = request.user
            exercise_type = form.cleaned_data["exercise_type"]
            correct_answer = form.cleaned_data["correct_answer"]
            user_answer = form.cleaned_data["user_answer"]

            data = prepare_exercises()

            form.save(
                user=user,
                exercise_type=exercise_type,
                correct_answer=correct_answer,
            )

            if user_answer == correct_answer:
                correct = True
                messages.success(request, _("Correct!"))
            else:
                correct = False
                messages.error(request, _("Sorry, your answer is incorrect"))

            return render(
                request,
                "exercises/show.html",
                {
                    "form": form,
                    "begin": data["sentence"][0],
                    "end": data["sentence"][1],
                    "button_status": "disabled",
                    "correct_answer": correct_answer if not correct else None
                },
            )

        else:
            return redirect("exercise_show")
