# registration/admin.py

from django.contrib import admin
from .models import (
    FoodPrepEquipment
)

# Register your models here.
myModels = [FoodPrepEquipment,]
# iterable list
admin.site.register(myModels)