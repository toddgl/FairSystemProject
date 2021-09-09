# registraion/urls.py
from django.urls import path, include
from .views import homepage_view, LoginPageView
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView  # v1


urlpatterns = [
    # path('', homepage_view, name='homepage'),
    # path('login/', LoginPageView.as_view(), name='login'),
    # path('login/', LoginView.as_view(template_name='registration/login.html')),
    path('',
         include('django.contrib.auth.urls')),  # v1
    path('',
         TemplateView.as_view(template_name='registration/home.html'), name='home'),  # v1
]
