# registration/urls.py
from django.urls import path, include

from registration.views import (
    FoodPrepEquipmentListView,
    FoodPrepEquipmentCreateView,
    FoodPrepEquipmentDetailUpdateView,
    FoodSaleTypeListView,
    FoodSaleTypeCreateView,
    FoodSaleTypeDetailUpdateView,
    StallCategoryListView,
    StallCategoryCreateView,
    StallCategoryDetailUpdateView,
    stall_registration_create,
    StallRegistrationCreateView,
    StallRegistrationUpdateView,
    food_registration,
    display_food_equipment,
    equipment_list,
    add_equipment,
    remove_equipment,
    edit_equipment,
    myfair_dashboard_view,
)

app_name = 'registration'

urlpatterns = [
    path('',
         include('django.contrib.auth.urls')),  # v1
    path('foodprepequipment/', FoodPrepEquipmentListView.as_view(), name='foodprepequipment-list'),
    path('foodprepequipment/,<int:pk>', FoodPrepEquipmentDetailUpdateView.as_view(), name='foodprepequipment-detail'),
    path('foodprepequipment/actionUrl/', FoodPrepEquipmentCreateView.as_view(), name='actionUrl'),
    path('foodsaletype/', FoodSaleTypeListView.as_view(), name='foodsaletype-list'),
    path('foodsaletype/,<int:pk>', FoodSaleTypeDetailUpdateView.as_view(), name='foodsaletype-detail'),
    path('foodsaletype/actionUrl/', FoodSaleTypeCreateView.as_view(), name='actionUrl'),
    path('stallcategory/', StallCategoryListView.as_view(), name='stallcategory-list'),
    path('stallcategory/,<int:pk>', StallCategoryDetailUpdateView.as_view(), name='stallcategory-detail'),
    path('stallcategory/actionUrl/', StallCategoryCreateView.as_view(), name='actionUrl'),
    path('stallregistration/', stall_registration_create, name='stallregistration-create'),
    path('stallregistration/,<int:pk>', StallRegistrationUpdateView.as_view(), name='stallregistration-detail'),
    path('myfair/', myfair_dashboard_view, name='myfair'),
    path('foodregistration',food_registration, name='food_registration'),
    path('foodequipment/', display_food_equipment, name='food-equipment'),
    path('foodequipment/list', equipment_list, name='equipment-list'),
    path('foodequipment/add', add_equipment, name='add-equipment'),
    path('foodequipment/<int:pk>/remove', remove_equipment, name='remove_equipment'),
    path('foodequipment/<int:pk>/edit', edit_equipment, name='edit_equipment'),
]
