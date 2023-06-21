from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from .forms import FileForm
from .models import File

# from english_exercises_app.mixins import MessagesMixin


class ExerciseCreateView(TemplateView):
    def get(self, request):
        return HttpResponse("Hi!")


class ExerciseShowView(TemplateView):
    def get(self, request):
        return HttpResponse("Hi!")


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
