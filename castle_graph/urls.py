from django.urls import path
from rest_framework.routers import DefaultRouter
from castle_graph.views import InviteView, AuthViewSet, GroupViewSet, SubmissionView, GifViewSet, CastleView, \
    SubmissionListView

app_name = 'castle_graph'
url = DefaultRouter()

url.register('invite', InviteView, basename='invite')
url.register('auth', AuthViewSet, basename='auth')
url.register('group', GroupViewSet, basename='group')
url.register('submission', SubmissionView, basename='submission')
url.register('gif', GifViewSet, basename='gif')
url.register('castles', CastleView, basename='castles')
url.register('submissions', SubmissionListView, basename='submissions')

urlpatterns = [] + url.get_urls()
