#accounts/adapter.py

from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect


class AccountAdapter(DefaultAccountAdapter):
    def pre_login(self, request, user, **kwargs):
        # Removes the check for user.is_active
        if not user.is_active:
            return self.respond_user_inactive(request, user)


    def respond_user_inactive(self, request, user):
        return HttpResponseRedirect(reverse_lazy('account_inactive'))


    def get_login_redirect_url(self, request):
        url = super(AccountAdapter, self).get_login_redirect_url(request)
        user = request.user
        role = user.get_role_display()
        if role == 'convener':
            url = reverse_lazy('fair:messages-dashboard')
        if role == 'stallholder':
            url = reverse_lazy('registration:stallregistration-dashboard')
        return url
