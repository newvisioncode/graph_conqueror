from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ContestGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)


class ContestUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
