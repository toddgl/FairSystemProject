# registration/admin.py

from django.contrib import admin
from .models import (
    FoodPrepEquipment,
    FoodSaleType,
    FoodRegistration,
    FoodPrepEquipReq,
    StallRegistration,
    StallCategory,
    CommentType,
    RegistrationComment,
    PowerConnection,
    RegistrationReview,
    ReviewErrorType
)

# Register your models here.
myModels = [
    FoodPrepEquipment,
    FoodSaleType,
    FoodRegistration,
    FoodPrepEquipReq,
    StallRegistration,
    StallCategory,
    CommentType,
    RegistrationComment,
    PowerConnection,
    RegistrationReview,
    ReviewErrorType
]
# iterable list
admin.site.register(myModels)