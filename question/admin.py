from django.contrib import admin

from question.models import Question, QuestionItem

# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionItem)