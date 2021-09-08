from django.shortcuts import render

# Create your views here.
# registration/views.py


def homepage_view(request):
    return render(request, 'registration/home.html')
