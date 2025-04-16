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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE, blank=True, null=True)
    payment_identifier = models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=False, null=False, blank=False)


class Castle(models.Model):
    castle_name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    identifier = models.IntegerField(unique=True, blank=False, null=False)
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    score = models.IntegerField(blank=False, null=False)
    neighbors = ArrayField(models.IntegerField(blank=False, null=False), blank=False, null=False)
    x = models.IntegerField(blank=False, null=False)
    y = models.IntegerField(blank=False, null=False)


class SubmissionLanguage(models.Model):
    language = models.CharField(max_length=100, blank=False, null=False)
    judge0_code = models.IntegerField(blank=False, null=False)


class Submission(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(ContestUser, on_delete=models.CASCADE)
    castle = models.ForeignKey(Castle, on_delete=models.CASCADE)
    language = models.ForeignKey(SubmissionLanguage, on_delete=models.CASCADE)
    source_code = models.FileField(upload_to="submissions/", blank=False, null=False)


class SubmissionItem(models.Model):
    class SubmissionResult(models.IntegerChoices):
        IN_QUEUE = 1, "In Queue"
        PROCESSING = 2, "Processing"
        ACCEPTED = 3, "Accepted"
        WRONG_ANSWER = 4, "Wrong Answer"
        TIME_LIMIT_EXCEEDED = 5, "Time Limit Exceeded"
        COMPILATION_ERROR = 6, "Compilation Error"
        RUNTIME_ERROR_SIGSEGV = 7, "Runtime Error (SIGSEGV)"
        RUNTIME_ERROR_SIGXFSZ = 8, "Runtime Error (SIGXFSZ)"
        RUNTIME_ERROR_SIGFPE = 9, "Runtime Error (SIGFPE)"
        RUNTIME_ERROR_SIGABRT = 10, "Runtime Error (SIGABRT)"
        RUNTIME_ERROR_NZEC = 11, "Runtime Error (NZEC)"
        RUNTIME_ERROR_OTHER = 12, "Runtime Error (Other)"
        INTERNAL_ERROR = 13, "Internal Error"
        EXEC_FORMAT_ERROR = 14, "Exec Format Error"
        UNKNOWN_ERROR = 15, "Unknown Error"

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, blank=False, null=False)
    question_item = models.ForeignKey(QuestionItem, on_delete=models.CASCADE, blank=False, null=False)
    token = models.CharField(max_length=50, blank=False, null=False)
    result = models.IntegerField(choices=SubmissionResult.choices, default=SubmissionResult.IN_QUEUE)
    runtime = models.FloatField(blank=True, null=True)


class CaptureCastle(models.Model):
    class CaptureCause(models.IntegerChoices):
        SOLVED = 0, _("Solved")
        CONQUERED = 1, _("Conquered")

    castle = models.ForeignKey(Castle, on_delete=models.CASCADE, blank=False, null=False)
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE, blank=False, null=False)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, blank=True, null=True)
    cause = models.IntegerField(blank=False, null=False, choices=CaptureCause.choices, default=CaptureCause.SOLVED)
    created = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)


class Payment(models.Model):
    user = models.ForeignKey(ContestUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tracking_code = models.CharField(max_length=64, blank=False, null=False)
    success = models.BooleanField(default=False)


class Invite(models.Model):
    class InviteStatus(models.IntegerChoices):
        PENDING = 0, _("pending")
        REJECTED = 1, _("rejected")
        ACCEPTED = 2, _("accepted")

    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(ContestUser, on_delete=models.CASCADE)
    uuid = models.UUIDField(auto_created=True, default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(blank=False, null=False, choices=InviteStatus.choices, default=InviteStatus.PENDING)

class Gif(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    confirmed = models.BooleanField(default=False)
    gif = models.FileField(upload_to="gifs")
