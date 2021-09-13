# registraion/urls.py
from django.urls import path, include
from django.views.generic.base import TemplateView  # v1


urlpatterns = [
    path('',
         include('django.contrib.auth.urls')),  # v1
    path('',
         TemplateView.as_view(template_name='registration/registration.html'),
         name='registration'),  # v1
]
