from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
# registration/views.py


def homepage_view(request):
    return render(request, 'registration/home.html')


class LoginPageView(TemplateView):
                    template_name = "registration/login.html"
