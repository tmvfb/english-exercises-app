from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.utils.translation import gettext_lazy as _

from .models import User


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "maxlength": "50",
                "class": "form-control",
                "placeholder": _("Username"),
            }
        )
        self.fields["username"].help_text = _(
            "Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only."  # noqa: E501
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Password")}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Repeat password")}
        )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username",
            "password1",
            "password2",
        ]


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})


class PasswordUpdateForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update({"class": "form-control mt-1"})
        self.fields["new_password1"].widget.attrs.update({"class": "form-control mt-1"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control mt-1"})
