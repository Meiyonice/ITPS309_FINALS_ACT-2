from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


# Every rule Django's password validators enforce, shown under each
# "new password" field (register and set-a-new-password alike).
PASSWORD_RULES = (
    "At least 8 characters",
    "Not all numbers",
    "Not too similar to your username or email",
    "Not a commonly used password",
)

PASSWORD_RULES_HELP = mark_safe(
    '<ul class="form-help-list">'
    + "".join(f"<li>{rule}</li>" for rule in PASSWORD_RULES)
    + "</ul>"
)


def _input(placeholder, autocomplete):
    return forms.TextInput(
        attrs={
            "class": "field-input",
            "placeholder": placeholder,
            "autocomplete": autocomplete,
        }
    )


def _password(placeholder, autocomplete):
    return forms.PasswordInput(
        attrs={
            "class": "field-input has-eye",
            "placeholder": placeholder,
            "autocomplete": autocomplete,
        }
    )


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=_input("Enter your username", "username"),
    )
    password = forms.CharField(
        label="Password",
        widget=_password("Enter your password", "current-password"),
    )
    remember_me = forms.BooleanField(
        label="Remember me",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "circle-check"}),
    )


class ForgotPasswordForm(forms.Form):
    """"Forgot password" form: the username and email on the account."""

    username = forms.CharField(
        label="Username",
        widget=_input("Enter your username", "username"),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "field-input",
                "placeholder": "Enter your email",
                "autocomplete": "email",
            }
        ),
    )

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        email = cleaned.get("email")
        if username and email:
            self.user = User.objects.filter(
                username__iexact=username.strip(), email__iexact=email.strip()
            ).first()
            if self.user is None:
                raise forms.ValidationError(
                    "No account matches that username and email. Check both and try again."
                )
        return cleaned


class ResetPasswordForm(SetPasswordForm):
    """New-password form reached from the emailed reset link."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "New password"
        self.fields["new_password1"].help_text = PASSWORD_RULES_HELP
        self.fields["new_password1"].widget = _password(
            "Enter your new password", "new-password"
        )
        self.fields["new_password2"].label = "Confirm new password"
        self.fields["new_password2"].widget = _password(
            "Re-enter your new password", "new-password"
        )


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        widget=_input("Enter your username", "username"),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "field-input",
                "placeholder": "Enter your email",
                "autocomplete": "email",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        help_text=PASSWORD_RULES_HELP,
        widget=_password("Enter your password", "new-password"),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=_password("Re-enter your password", "new-password"),
    )
    terms = forms.BooleanField(
        label="I accept the terms of the agreement.",
        required=True,
        error_messages={
            "required": "You must accept the terms of the agreement.",
        },
        widget=forms.CheckboxInput(attrs={"class": "circle-check"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
