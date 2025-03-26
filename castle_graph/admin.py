from django.contrib import admin

from castle_graph.models import Submission, Castle, CaptureCastle, SubmissionItem

# Register your models here.
admin.site.register(Submission)
admin.site.register(Castle)
admin.site.register(SubmissionItem)
admin.site.register(CaptureCastle)