# from django.contrib import messages
# from django.urls import reverse_lazy
# from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.http import HttpResponse
# from english_exercises_app.mixins import MessagesMixin


class TaskCreateView(TemplateView):
    def get(self, request):
        return HttpResponse('Hi!')
