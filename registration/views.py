from django.shortcuts import render

# Create your views here.
# registration/views.py
from django.http import HttpResponse


def homepage_view(request):
    return render(request,'registration/registration.html')
