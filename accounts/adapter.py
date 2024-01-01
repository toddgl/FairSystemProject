#accounts/adapter.py

from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        url = super(AccountAdapter, self).get_login_redirect_url(request)
        user = request.user
        role = user.get_role_display()
        if role == 'convener':
            url = reverse_lazy('fair:messages-dashboard')
        if role == 'stallholder':
            url = reverse_lazy('registration:stallregistration-dashboard')
        return url
