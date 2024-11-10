# search/urls.py
from django.urls import path

from search.views import (
    stallholder_search_view,
    stallholder_list_search_view,
    stallholder_registration_search_view,
    stallholder_siteallocation_search_view,
    create_siteallocation_search_view,
    stallholder_history_search_view,
    stallholder_payment_history_search_view
)

app_name = 'search'

urlpatterns = [

]

htmx_urlpatterns = [
    path('search-stallholders-history/', stallholder_history_search_view, name='search-stallholders-history'),
    path('search-stallholders/',stallholder_search_view, name='search-stallholders'),
    path('search-stallholders-list/', stallholder_list_search_view, name='search-stallholders-list'),
    path('search-stallholders-registration/', stallholder_registration_search_view, name='search-stallholders-registration'),
    path('search-stallholders-siteallocations/', stallholder_siteallocation_search_view, name='search-stallholders-siteallocations'),
    path('create-siteallocation/', create_siteallocation_search_view, name='create-siteallocation'),
    path('search-stallholders-paymenthistory/', stallholder_payment_history_search_view, name='search-stallholders-paymenthistory'),
]

urlpatterns += htmx_urlpatterns

