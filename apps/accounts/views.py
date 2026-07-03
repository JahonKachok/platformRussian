from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, FormView, UpdateView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import User
from .forms import RegisterForm, LoginForm, ProfileForm, ForgotPasswordForm, ResetPasswordForm
from .services import send_verification_email, send_password_reset_email, verify_email_token, verify_reset_token


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('courses:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        send_verification_email(user, self.request)
        messages.success(self.request, _('Account created! Please check your email to verify your account.'))
        return super().form_valid(form)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('courses:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('courses:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        login(self.request, user)
        user.last_active = timezone.now()
        user.save(update_fields=['last_active'])
        next_url = self.request.GET.get('next', str(self.success_url))
        return redirect(next_url)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

    def post(self, request):
        logout(request)
        return redirect('home')


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully!'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            from apps.gamification.models import UserProgress, Achievement
            ctx['progress'] = UserProgress.objects.get(user=self.request.user)
            ctx['achievements'] = Achievement.objects.filter(
                userachievement__user=self.request.user
            ).order_by('-userachievement__earned_at')[:6]
        except Exception:
            ctx['progress'] = None
            ctx['achievements'] = []
        return ctx


class ForgotPasswordView(FormView):
    form_class = ForgotPasswordForm
    template_name = 'accounts/forgot_password.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user, self.request)
        except User.DoesNotExist:
            pass
        messages.success(self.request, _('Password reset link sent to your email.'))
        return super().form_valid(form)


class ResetPasswordView(FormView):
    form_class = ResetPasswordForm
    template_name = 'accounts/reset_password.html'

    def get_user(self):
        token = self.kwargs.get('token')
        return verify_reset_token(token)

    def dispatch(self, request, *args, **kwargs):
        if not self.get_user():
            messages.error(request, _('Invalid or expired reset link.'))
            return redirect('accounts:forgot-password')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.get_user()
        user.set_password(form.cleaned_data['password1'])
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()
        messages.success(self.request, _('Password changed successfully! Please login.'))
        return redirect('accounts:login')


class VerifyEmailView(View):
    def get(self, request, token):
        user = verify_email_token(token)
        if user:
            messages.success(request, _('Email verified successfully!'))
        else:
            messages.error(request, _('Invalid verification link.'))
        return redirect('accounts:login')
