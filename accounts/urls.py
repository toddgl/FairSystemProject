# accounts/urls.py

from django.urls import path
from .views import (
    customuser_update_view,
)

app_name = 'accounts'

urlpatterns = [
    path('accounts/update', customuser_update_view, name='user-update'),
]
