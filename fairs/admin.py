from django.contrib import admin
from .models import (
    Fair,
    Event,
)

# Register your models here.
myModels = [Fair, Event]  # iterable list
admin.site.register(myModels)
