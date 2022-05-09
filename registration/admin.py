# registration/admin.py

from django.contrib import admin
from .models import (
    FoodPrepEquipment,
    FoodSaleType,
    FoodRegistration,
    FoodPrepEquipReq,
    StallRegistration,
    StallCategory,
    RegistrationComment,
)

# Register your models here.
myModels = [FoodPrepEquipment, FoodSaleType, FoodRegistration, FoodPrepEquipReq, StallRegistration, StallCategory,  RegistrationComment]
# iterable list
admin.site.register(myModels)