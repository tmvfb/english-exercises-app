from django.urls import reverse_lazy
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
            return redirect(reverse_lazy("exercise_upload"))


class ExerciseCreateView(TemplateView):
    def get(self, request):
        form = FilterForm()
        return render(request, "exercises/create.html", {"form": form})

    def post(self, request):
        form = FilterForm(request.POST)

        if form.is_valid():
            # TODO: more options to come
            count = form.cleaned_data['count']  # integer
            pos = form.cleaned_data['pos']  # list
            ex_type = form.cleaned_data['type_']  # string
            length = form.cleaned_data['length']  # integer

            exercises = prepare_exercises(
                count,
                pos,
                ex_type,
                length
            )

            return HttpResponse(exercises)

        else:
            return redirect("exercise_show")


class ExerciseShowView(TemplateView):
    def get(self, request):
        form = TypeInExercise()
        return render(request, "exercises/show.html", {"form": form})
