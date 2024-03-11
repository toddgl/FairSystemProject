# faq/urls.py

from django.urls import path

from faq.views import (
    FaqCreateView,
    FaqDetailUpdateView,
    FaqListView
)

app_name = 'faq'  # This is the namespace, so you can reverse urls with faq:*

urlpatterns = [
    path('faq/', FaqListView.as_view(), name='faq-list'),
    path('faq/actionUrl/', FaqCreateView.as_view(), name='actionUrl'),
    path('faq/<int:pk>', FaqDetailUpdateView.as_view(), name='faq-detail'),
]
