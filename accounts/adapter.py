#accounts/adapter.py

from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)

class AccountAdapter(DefaultAccountAdapter):
    def pre_login(self, request, user, **kwargs):
        # Remove the check for user.is_active
        # or add your custom logic here
        print('Got to the adapter')
        if not user.is_active:
            return self.respond_user_inactive(request, user)
        # super().pre_login(request, user, **kwargs)


    def respond_user_inactive(self, request, user):
        return HttpResponseRedirect(reverse_lazy('account_inactive'))


    def get_login_redirect_url(self, request):
        print('Got to the get_login_redirect_url')
        url = super(AccountAdapter, self).get_login_redirect_url(request)
        user = request.user
        role = user.get_role_display()
        print(f"Username: {user}, User role: {role}")
        if role == 'convener':
            url = reverse_lazy('fair:messages-dashboard')
        if role == 'stallholder':
            url = reverse_lazy('registration:stallregistration-dashboard')
        print(f"Redirect URL: {url}")
        return url
