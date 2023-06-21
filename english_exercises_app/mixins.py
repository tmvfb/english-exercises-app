from django.contrib import messages


class MessagesMixin:
    """
    Redefines validation functions to show flash messages.
    Adds bootstrap-js green checkmarks and red warning signs for forms.
    """
    # success_message = None

    def form_valid(self, form):
        messages.success(
            self.request, _(self.success_message)
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        for field in form:
            if field.errors:
                form.fields[field.name].widget.attrs["class"] += " is-invalid"
            else:
                form.fields[field.name].widget.attrs["class"] += " is-valid"
        messages.error(
            self.request,
            _("Something went wrong. Please check the entered data"),
        )
        return super().form_invalid(form)
