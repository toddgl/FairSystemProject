# pages/urls.py
from django.urls import path

from .views import NoticePageView, FaqPageView

urlpatterns = [
    path('', NoticePageView.as_view(), name='notice-list'),
    path('faq', FaqPageView.as_view(), name='faq'),
]
