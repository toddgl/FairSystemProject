# fairs/admin.py

from django.contrib import admin
from .models import (
    Fair,
    Event,
    Site,
    Location,
    Zone,
    EventSite,
    InventoryItem,
    InventoryItemFair,
    PowerBox,
    EventPower
)

# Register your models here.
myModels = [Fair, Event, Site, Location, Zone, EventSite, InventoryItem, InventoryItemFair, PowerBox, EventPower]
# iterable list
admin.site.register(myModels)
