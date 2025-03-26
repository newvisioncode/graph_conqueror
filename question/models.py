from django.db import models
from django_quill.fields import QuillField


class Question(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    question = QuillField(blank=False, null=False)
    level = models.SmallIntegerField(blank=False, null=False, default=1)


class QuestionItem(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=False, blank=False)
    input = models.TextField(blank=False, null=False)
    output = models.TextField(blank=False, null=False)
