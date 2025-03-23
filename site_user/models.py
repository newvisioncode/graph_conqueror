from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField("ایمیل", blank=True, unique=True)
    phone_number = models.CharField("شماره همراه", max_length=11, unique=True, validators=[RegexValidator("^09\d{9}$")])