from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField("email", blank=True, unique=True)
    phone_number = models.CharField("phone_number", max_length=11, blank=False, unique=True,
                                    validators=[RegexValidator(r"^09\d{9}$")])
