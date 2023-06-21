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
        return HttpResponse('Hi!')


class ExerciseShowView(TemplateView):
    def get(self, request):
        return HttpResponse('Hi!')


class ExerciseUploadView(TemplateView):
    def get(self, request):
        form = FileForm()
        return render(request, 'exercises/upload.html', {'form': form})

    def post(self, request):
        form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            f = request.FILES["file"]
            with open("temp.txt", "wb+") as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            return render(request, 'exercises/upload.html', {'form': form})

        else:
            messages.warning(request, _('Something went wrong'))
            return redirect(reverse_lazy('exercise_upload'))
