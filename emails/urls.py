# emails/urls.py

from django.urls import path

from emails.views import (
    email_history_dashboard_view,
    email_history_listview
)

app_name = 'emails'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('emails/', email_history_dashboard_view, name='email-dashboard'),
    path('emails/list/', email_history_listview, name='email-list')
]

