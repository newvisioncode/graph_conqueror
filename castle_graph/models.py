import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ContestGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)


class ContestUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)


class Payment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    success = models.BooleanField(default=False)


class Invite(models.Model):
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(ContestUser, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    time_created = models.DateTimeField(auto_now_add=True)
