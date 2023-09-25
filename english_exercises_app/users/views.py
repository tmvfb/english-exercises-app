from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, TemplateView

from english_exercises_app.mixins import MessagesMixin

from .forms import LoginForm, PasswordUpdateForm, RegistrationForm
from .models import User


class UserCreateView(MessagesMixin, CreateView):
    form_class = RegistrationForm
    template_name = "users/create.html"
    success_message = _("User created successfully!")
    success_url = reverse_lazy("user_login")


class UserPasswordUpdateView(MessagesMixin, LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordUpdateForm
    model = User
    template_name = "users/update.html"
    success_message = _("Password updated successfully!")
    permission_denied_message = _("Please log in.")
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("user_login")


class UserDeleteView(MessagesMixin, LoginRequiredMixin, DeleteView):
    template_name = "users/delete.html"
    model = User
    success_message = _("User deleted successfully!")
    permission_denied_message = _("Please log in.")
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("user_login")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.User == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return redirect(success_url)
        else:
            messages.error(self.request, _("You may only delete your own profile."))
            return redirect("home")


class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "users/settings.html"
    login_url = reverse_lazy("user_login")
    permission_denied_message = _("Please log in.")


class UserLoginView(MessagesMixin, LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    success_message = _("Logged in successfully!")


class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _("You are logged out"))
        return super().dispatch(request, *args, **kwargs)
