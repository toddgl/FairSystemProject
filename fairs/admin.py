from django.contrib import admin
from .models import (
    Fair,
    Event,
    Site,
    Zone,
    EventSite,
    InventoryItem,
    InventoryItemFair,

)

# Register your models here.
myModels = [Fair, Event, Site, Zone, EventSite, InventoryItem, InventoryItemFair]  # iterable list
admin.site.register(myModels)
