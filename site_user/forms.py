from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(forms.ModelForm):
    phone_number = forms.RegexField(regex=r'^09\d{9}$', label="شماره همراه")
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("first_name", "last_name", "username", "email", "phone_number")
