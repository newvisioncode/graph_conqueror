from django.urls import path
from rest_framework.routers import DefaultRouter

from castle_graph import consumers
from castle_graph.views import InviteView, AuthViewSet, GroupViewSet, SubmissionView, GifViewSet

app_name = 'castle_graph'
url = DefaultRouter()

url.register('invite', InviteView, basename='invite')
url.register('auth', AuthViewSet, basename='auth')
url.register('group', GroupViewSet, basename='group')
url.register('submission', SubmissionView, basename='submission')
url.register('gif', GifViewSet, basename='gif')

urlpatterns = [] + url.get_urls()

websocket_urlpatterns = [
    path("ws/", consumers.ChatConsumer.as_asgi()),
]
