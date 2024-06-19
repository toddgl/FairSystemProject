# notices/urls.py

from django.urls import path

from notices.views import (
    NoticeCreateView,
    NoticeDetailUpdateView,
    notice_listview
)

app_name = 'notices'  # This is the namespace, so you can reverse urls with notices:*

urlpatterns = [
    path('notice/', notice_listview, name='notice-list'),
    path('notice/actionUrl/', NoticeCreateView.as_view(), name='actionUrl'),
    path('notice/<int:pk>', NoticeDetailUpdateView.as_view(), name='notice-detail'),
]
