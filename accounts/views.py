# accounts/view.py
from django.views.generic.edit import UpdateView
from .models import CustomUser
from .forms import CustomUserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_update.html'
    success_url = '/'

    def get_object(self):
        return self.request.user
