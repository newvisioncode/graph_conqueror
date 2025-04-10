from django.contrib import admin

from castle_graph.models import Submission, Castle, CaptureCastle, SubmissionItem, ContestUser, ContestGroup, \
    SubmissionLanguage, Gif

# Register your models here.
admin.site.register(Submission)
admin.site.register(Castle)
admin.site.register(SubmissionItem)
admin.site.register(CaptureCastle)
admin.site.register(ContestUser)
admin.site.register(ContestGroup)
admin.site.register(SubmissionLanguage)
admin.site.register(Gif)
