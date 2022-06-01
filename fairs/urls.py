# fairs/urls.py


from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from fairs.views import (
    FairListView,
    FairCreateView,
    FairDetailUpdateView,
    EventCreateView,
    EventListView,
    EventDetailUpdateView,
    EventPowerCreateView,
    EventPowerListView,
    EventPowerDetailUpdateView,
    LocationCreateView,
    LocationDetailUpdateView,
    LocationListView,
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
    InventoryItemFairListView,
    InventoryItemFairCreateView,
    InventoryItemFairDetailUpdateView,
    PowerBoxListView,
    PowerBoxDetailUpdateView,
    PowerBoxCreateView,
    site_dashboard_view
)

app_name = 'fair'  # This is the namespace so you can reverse urls with fair:*

urlpatterns = [

    path('fair/', FairListView.as_view(), name='fair-list'),
    path('fair/<int:pk>', FairDetailUpdateView.as_view(), name='fair-detail'),
    path('event/', EventListView.as_view(), name='event-list'),
    path('event/<int:pk>', EventDetailUpdateView.as_view(), name='event-detail'),
    path('location/', LocationListView.as_view(), name='location-list'),
    path('location/,<int:pk>', LocationDetailUpdateView.as_view(), name='location-detail'),
    path('zone/', ZoneListView.as_view(), name='zone-list'),
    path('zone/,<int:pk>', ZoneDetailUpdateView.as_view(), name='zone-detail'),
    path('site/', SiteListView.as_view(), name='site-list'),
    path('site/,<int:pk>', SiteDetailUpdateView.as_view(), name='site-detail'),
    path('eventsite/', EventSiteListView.as_view(), name='eventsite-list'),
    path('eventsite/,<int:pk>', EventSiteDetailUpdateView.as_view(), name='eventsite-detail'),
    path('inventoryitem/', InventoryItemListView.as_view(), name='inventoryitem-list'),
    path('inventoryitem/,<int:pk>', InventoryItemDetailUpdateView.as_view(), name='inventoryitem-detail'),
    path('inventoryitemfair/', InventoryItemFairListView.as_view(), name='inventoryitemfair-list'),
    path('inventoryitemfair/,<int:pk>', InventoryItemFairDetailUpdateView.as_view(), name='inventoryitemfair-detail'),
    path('powerbox/', PowerBoxListView.as_view(), name='powerbox-list'),
    path('powerbox/,<int:pk>', PowerBoxDetailUpdateView.as_view(), name='powerbox-detail'),
    path('eventpower/', EventPowerListView.as_view(), name='eventpower-list'),
    path('eventpower/,<int:pk>', EventPowerDetailUpdateView.as_view(), name='eventpower-detail'),
    path('dashboard/', site_dashboard_view, name='site-dashboard'),
    path('dashboard/actionUrl/', EventSiteListView.as_view(), name='actionUrl'),
    path('fair/actionUrl/', FairCreateView.as_view(), name='actionUrl'),
    path('event/actionUrl/', EventCreateView.as_view(), name='actionUrl'),
    path('location/actionUrl/', LocationCreateView.as_view(), name='actionUrl'),
    path('zone/actionUrl/', ZoneCreateView.as_view(), name='actionUrl'),
    path('site/actionUrl/', SiteCreateView.as_view(), name='actionUrl'),
    path('eventsite/actionUrl/', EventSiteCreateView.as_view(), name='actionUrl'),
    path('inventoryitem/actionUrl/', InventoryItemCreateView.as_view(), name='actionUrl'),
    path('inventoryitemfair/actionUrl/', InventoryItemFairCreateView.as_view(), name='actionUrl'),
    path('powerbox/actionUrl/', PowerBoxCreateView.as_view(), name='actionUrl'),
    path('eventpower/actionUrl/', EventPowerCreateView.as_view(), name='actionUrl'),
]
