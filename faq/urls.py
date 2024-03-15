# faq/urls.py

from django.urls import path

from faq.views import (
    FaqCreateView,
    FaqDetailUpdateView,
    faq_listview
)

app_name = 'faq'  # This is the namespace, so you can reverse urls with faq:*

urlpatterns = [
    path('faq/', faq_listview, name='faq-list'),
    path('faq/actionUrl/', FaqCreateView.as_view(), name='actionUrl'),
    path('faq/<int:pk>', FaqDetailUpdateView.as_view(), name='faq-detail'),
]
