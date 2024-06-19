# config/urls.py

"""FairSystemProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # import include function
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from search.views import search_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),  # pages at the root URL
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    path('', include('faq.urls')),
    path('', include('notices.urls')),
    path('payment/', include('payment.urls')),
    path('registration/', include('registration.urls')),
    path('', include('fairs.urls')),
    path('',include('search.urls')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
