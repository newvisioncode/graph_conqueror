from django.urls import path
from rest_framework.routers import DefaultRouter
from castle_graph.views import InviteView

app_name = 'castle_graph'
url = DefaultRouter()

url.register('invite', InviteView)

urlpatterns = [] + url.get_urls()
