# from django.urls import reverse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.contrib import messages
from .forms import FileForm, FilterForm, TypeInExercise
from .models import File, Memory
from text_processing.prepare_data import prepare_exercises

# from english_exercises_app.mixins import MessagesMixin


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
            # delete previous file and db entry, if exist
            file = File.objects.filter(user=request.user).first()
            if file is not None:
                file.file.delete()
                file.delete()

            file_instance = File(file=request.FILES["file"], user=request.user)
            file_instance.save()
            messages.success(request, _("File uploaded successfully!"))
            return render(request, "exercises/upload.html", {"form": form})

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
        form = FilterForm(request.POST)

        if form.is_valid():
            # # TODO: more options to come
            # count = form.cleaned_data["count"]  # integer
            # pos = form.cleaned_data["pos"]  # list
            # ex_type = form.cleaned_data["exercise_type"]  # string
            # length = form.cleaned_data["length"]  # integer
            form.save(user=request.user)
            return redirect("exercise_show")

        else:
            messages.error(request, _("Please select all the parameters"))
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
        print(filepath)

        # retrieve current params for exercise generation
        params = Memory.objects.filter(user=request.user).first()
        kwargs = {
            field.name: getattr(params, field.name)
            for field in params._meta.fields
        }

        # prepare exercises and populate form fields
        data = prepare_exercises(filepath, **kwargs)
        form = TypeInExercise(
            initial={
                "exercise_type": data["exercise_type"],
                "correct_answer": data["correct_answer"],
                "begin": data["sentence"][0],
                "end": data["sentence"][1]
            }
        )
        return render(request, "exercises/show.html", {"form": form})

    def post(self, request):
        form = TypeInExercise(request.POST)

        if form.is_valid():
            user = request.user
            correct_answer = form.cleaned_data["correct_answer"]
            user_answer = form.cleaned_data["user_answer"]

            form.save(user=user)

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
                    "button_status": "disabled",
                    "correct_answer": correct_answer if not correct else None,
                },
            )

        else:
            return redirect("exercise_show")
