from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse
from django.views.generic import CreateView

from .forms import SignUpForm

User = get_user_model()


# Create your views here.

class Login(LoginView):
    template_name = 'user/login.html'
    next_page = 'index'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True
    redirect_field_name = 'index'


class Logout(LogoutView):
    next_page = 'index'
    redirect_field_name = 'index'


class SignUp(CreateView):
    template_name = 'user/login.html'
    model = User
    form_class = SignUpForm
    next_page = 'index'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super(SignUp, self).form_valid(form)

    def get_success_url(self):
        return reverse("index")




