import uuid
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import User


def send_verification_email(user, request):
    token = str(user.email_verification_token)
    scheme = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    link = f'{scheme}://{domain}/accounts/verify-email/{token}/'
    send_mail(
        subject=str(_('Verify your Rustili account')),
        message=str(_('Click the link to verify your email: ')) + link,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_password_reset_email(user, request):
    token = uuid.uuid4()
    user.password_reset_token = token
    user.password_reset_expires = timezone.now() + timezone.timedelta(hours=2)
    user.save(update_fields=['password_reset_token', 'password_reset_expires'])

    scheme = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    link = f'{scheme}://{domain}/accounts/reset-password/{token}/'
    send_mail(
        subject=str(_('Reset your Rustili password')),
        message=str(_('Click the link to reset your password: ')) + link,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def verify_email_token(token):
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
        return user
    except User.DoesNotExist:
        return None


def verify_reset_token(token):
    try:
        user = User.objects.get(password_reset_token=token)
        if user.password_reset_expires and timezone.now() > user.password_reset_expires:
            return None
        return user
    except User.DoesNotExist:
        return None
