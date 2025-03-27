from django.urls import path

from . import views

app_name = 'castle_graph'

urlpatterns = [
    path('invite/create/', views.CreateInviteView.as_view(), name='invite-create'),
    path('invite/accept/', views.AcceptInviteView.as_view(), name='invite-accept'),
]