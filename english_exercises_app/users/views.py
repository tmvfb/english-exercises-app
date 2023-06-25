from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from english_exercises_app.mixins import MessagesMixin

from .forms import LoginForm, RegistrationForm


class UserCreateView(MessagesMixin, CreateView):
    form_class = RegistrationForm
    template_name = "users/create.html"
    success_message = _("User created successfully!")
    success_url = reverse_lazy("user_login")


class UserLoginView(MessagesMixin, LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    success_message = _("Logged in successfully!")


class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _("You are logged out"))
        return super().dispatch(request, *args, **kwargs)
