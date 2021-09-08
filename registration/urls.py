# registraion/urls.py
from django.urls import path
from .views import homepage_view
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('login/',
         LoginView.as_view(template_name='registration/login.html')),
    #    url(r'login/$',
    #    LoginView.as_view(template_name='registration/login.html'))
]
