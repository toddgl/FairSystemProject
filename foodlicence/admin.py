# foodlicence/admin.py
from django.contrib import admin
from .models import (
    FoodLicenceBatch,
    FoodLicence
)
# Register your models here.
myModels = [ FoodLicenceBatch, FoodLicence ]
# iterable list
admin.site.register(myModels)
