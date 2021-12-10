# accounts/urls.py

from django.urls import path
from .views import customuser_update_view

app_name = 'accounts'

urlpatterns = [
    # <pk> is identification for id field,
    # <slug> can also be used
    # path('update', CustomUserUpdateView.as_view(), name='update'),
    path('update', customuser_update_view, name='user-update'),
]
