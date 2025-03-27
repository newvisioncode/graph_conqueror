import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from question.models import Question, QuestionItem

User = get_user_model()


class ContestGroup(models.Model):
    lead_user = models.OneToOneField('castle_graph.ContestUser', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, unique=True)


class ContestUser(models.Model):
    user = models.OneToOne(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    payment_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Castle(models.Model):
    castle_name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.IntegerField(blank=False, null=False)
    neighbors = ArrayField(models.CharField(max_length=100, blank=False), blank=False, null=False)


class Submission(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(ContestUser, on_delete=models.CASCADE)
    castle = models.ForeignKey(Castle, on_delete=models.CASCADE)


class SubmissionItem(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, blank=False, null=False)
    question_item = models.ForeignKey(QuestionItem, on_delete=models.CASCADE, blank=False, null=False)
    token = models.CharField(max_length=255, blank=False, null=False)
    result = models.CharField(max_length=255, blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)


class CaptureCastle(models.Model):
    class CaptureCause(models.IntegerChoices):
        SOLVED = 0, _("Solved")
        CONQUERED = 1, _("Conquered")

    castle = models.ForeignKey(Castle, on_delete=models.CASCADE, blank=False, null=False)
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE, blank=False, null=False)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, blank=True, null=True)
    cause = models.IntegerField(blank=False, null=False, choices=CaptureCause.choices, default=CaptureCause.SOLVED)
    created = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    user = models.ForeignKey(ContestUser, on_delete=models.CASCADE)
    success = models.BooleanField(default=False)


class Invite(models.Model):
    class InviteStatus(models.IntegerChoices):
        PENDING = 0, _("pending")
        REJECTED = 1, _("rejected")
        ACCEPTED = 2, _("accepted")

    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(ContestUser, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    time_created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(blank=False, null=False, choices=InviteStatus.choices, default=InviteStatus.PENDING)
