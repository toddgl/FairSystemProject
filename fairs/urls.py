# fairs/urls.py


from django.urls import path

from fairs.views import (
    FairListView,
    FairCreateView,
    FairDetailUpdateView,
    EventCreateView,
    EventListView,
    EventDetailUpdateView,
    ZoneCreateView,
    ZoneListView,
    ZoneDetailUpdateView,
    SiteCreateView,
    SiteListView,
    SiteDetailUpdateView,
    EventSiteCreateView,
    EventSiteListView,
    EventSiteDetailUpdateView,
    InventoryItemCreateView,
    InventoryItemListView,
    InventoryItemDetailUpdateView,
    SiteDashboardView
)

app_name = 'fair'  # This is the namespace so you can reverse urls with fair:*

urlpatterns = [

    path('fair/', FairListView.as_view(), name='fair-list'),
    path('fair/<int:pk>', FairDetailUpdateView.as_view(), name='fair-detail'),
    path('event/', EventListView.as_view(), name='event-list'),
    path('event/<int:pk>', EventDetailUpdateView.as_view(), name='event-detail'),
    path('zone/', ZoneListView.as_view(), name='zone-list'),
    path('zone/,<int:pk>', ZoneDetailUpdateView.as_view(), name='zone-detail'),
    path('site/', SiteListView.as_view(), name='site-list'),
    path('site/,<int:pk>', SiteDetailUpdateView.as_view(), name='site-detail'),
    path('eventsite/', EventSiteListView.as_view(), name='eventsite-list'),
    path('eventsite/,<int:pk>', EventSiteDetailUpdateView.as_view(), name='eventsite-detail'),
    path('inventoryitem/', InventoryItemListView.as_view(), name='inventoryitem-list'),
    path('inventoryitem/,<int:pk>', InventoryItemDetailUpdateView.as_view(), name='inventoryitem-detail'),
    path('dashboard/', SiteDashboardView.as_view(), name='site-dashboard'),
    path('dashboard/actionURL/', EventSiteListView.as_view(), name='actionURL'),
    path('fair/actionUrl/', FairCreateView.as_view(), name='actionUrl'),
    path('event/actionUrl/', EventCreateView.as_view(), name='actionUrl'),
    path('zone/actionUrl/', ZoneCreateView.as_view(), name='actionUrl'),
    path('site/actionUrl/', SiteCreateView.as_view(), name='actionUrl'),
    path('eventsite/actionUrl/', EventSiteCreateView.as_view(), name='actionUrl'),
    path('inventoryitem/actionUrl/', InventoryItemCreateView.as_view(), name='actionUrl'),
]
