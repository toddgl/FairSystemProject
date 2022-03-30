# pages/urls.py
from django.urls import path

from .views import HomePageView, FaqPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('faq', FaqPageView.as_view(), name='faq'),
]
