from django.urls import path
from .views import SignUpView, CustomAuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import *

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
]