# search/urls.py
from django.urls import path, include

from search.views import (
    stallholder_search_view,
    stallholder_list_search_view
)

app_name = 'search'

urlpatterns = [

]

htmx_urlpatterns = [
    path('search-stallholders/',stallholder_search_view, name='search-stallholders'),
    path('search-stallholders-list', stallholder_list_search_view, name='search-stallholders-list'),

]

urlpatterns += htmx_urlpatterns

