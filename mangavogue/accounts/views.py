from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm

User = get_user_model()


class AppLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(0)
        return response


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. You can log in now.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def forgot_password_view(request):
    """Step 1: confirm the account with its username and email."""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            request.session["password_reset_user"] = form.user.pk
            return redirect("password_reset_confirm")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/password_reset_form.html", {"form": form})


def set_new_password_view(request):
    """Step 2: the verified account picks a new password."""
    user_id = request.session.get("password_reset_user")
    user = User.objects.filter(pk=user_id).first() if user_id else None
    if user is None:
        messages.error(request, "Verify your username and email first.")
        return redirect("password_reset")

    if request.method == "POST":
        form = ResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            request.session.pop("password_reset_user", None)
            return redirect("password_reset_complete")
    else:
        form = ResetPasswordForm(user)

    return render(
        request,
        "accounts/password_reset_confirm.html",
        {"form": form, "reset_username": user.get_username()},
    )


def password_reset_complete_view(request):
    return render(request, "accounts/password_reset_complete.html")


@login_required
def home(request):
    return render(request, "accounts/home.html")
