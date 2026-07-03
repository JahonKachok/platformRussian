from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label=_('First name'),
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': _('First name'), 'autocomplete': 'given-name'})
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': _('Last name'), 'autocomplete': 'family-name'})
    )
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': _('Email address'), 'autocomplete': 'email'})
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Password'), 'autocomplete': 'new-password'})
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Confirm password'), 'autocomplete': 'new-password'})
    )
    agree_terms = forms.BooleanField(
        label=_('I agree to the Terms of Service'),
        required=True
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].split('@')[0] + '_' + User.objects.count().__str__()
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': _('Email address'), 'autocomplete': 'email'})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Password'), 'autocomplete': 'current-password'})
    )
    remember_me = forms.BooleanField(label=_('Remember me'), required=False)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'phone', 'date_of_birth', 'country', 'language', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': _('First name')}),
            'last_name': forms.TextInput(attrs={'placeholder': _('Last name')}),
            'bio': forms.Textarea(attrs={'placeholder': _('Tell about yourself...'), 'rows': 4}),
            'phone': forms.TextInput(attrs={'placeholder': '+998 XX XXX-XX-XX'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'country': forms.TextInput(attrs={'placeholder': _('Country')}),
        }


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': _('Enter your email address')})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('No account found with this email.'))
        return email


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('New password')})
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Confirm new password')})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('Passwords do not match.'))
        return cleaned_data
