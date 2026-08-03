from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):

    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "block w-full rounded-lg border border-gray-300 bg-gray-50 text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:text-white hover:file:bg-blue-700"
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "avatar"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = "Minimum 8 characters."
        self.fields["password2"].help_text = "Re-enter your password."

        self.fields["username"].widget.attrs.update({"placeholder": "Username"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm Password"})

        for field in self.fields.values():
            if field.label != "Avatar":
                field.widget.attrs.update({
                    "class": "w-full rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                })


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500",
            })