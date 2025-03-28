from django.urls import path
from rest_framework.routers import DefaultRouter
from castle_graph.views import InviteView, AuthViewSet

app_name = 'castle_graph'
url = DefaultRouter()

url.register('invite', InviteView, basename='invite')
url.register('auth', AuthViewSet, basename='auth')

urlpatterns = [] + url.get_urls()
