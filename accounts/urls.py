# accounts/urls.py

from django.urls import path
from .views import (
    customuser_update_view,
    profile_view
)

app_name = 'accounts'

urlpatterns = [
    # <pk> is identification for id field,
    # <slug> can also be used
    # path('update', CustomUserUpdateView.as_view(), name='update'),
    path('accounts/profile/', profile_view, name='profile'),
    path('accounts/update', customuser_update_view, name='user-update'),
]
