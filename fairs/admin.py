# fairs/admin.py

from django.contrib import admin
from .models import (
    Fair,
    Event,
    Site,
    Location,
    Zone,
    ZoneMap,
    EventSite,
    InventoryItem,
    InventoryItemFair,
    PowerBox,
    EventPower,
    SiteAllocation
)

# Register your models here.
myModels = [Fair, Event, Site, Location, Zone, ZoneMap, EventSite, SiteAllocation, InventoryItem, InventoryItemFair, PowerBox, EventPower]
# iterable list
admin.site.register(myModels)
