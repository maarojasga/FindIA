from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from .forms import SignUpForm, CustomAuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

def custom_logout(request):
    logout(request)
    return redirect('login')
#@login_required
class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_url = '/accounts/'