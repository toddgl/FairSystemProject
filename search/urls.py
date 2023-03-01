# search/urls.py
from django.urls import path, include

from search.views import (
    stallholder_search_view,
    stallholder_list_search_view,
    stallholder_registration_search_view
)

app_name = 'search'

urlpatterns = [

]

htmx_urlpatterns = [
    path('search-stallholders/',stallholder_search_view, name='search-stallholders'),
    path('search-stallholders-list', stallholder_list_search_view, name='search-stallholders-list'),
    path('search-stallholders-registration', stallholder_registration_search_view, name='search-stallholders-registration'),

]

urlpatterns += htmx_urlpatterns

